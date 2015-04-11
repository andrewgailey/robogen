import time
import os
import sys
import cPickle as pickle
import argparse
from argparse import RawTextHelpFormatter
from multiprocessing.pool import Pool
from multiprocessing.process import Process
import threading
import Queue
import msvcrt
import cProfile, pstats, StringIO

from rgkit import run as rgrun
from rgkit.game import Player

from generation import Generation
import constants


progress_q = Queue.Queue(maxsize=1)
early_end_q = Queue.Queue(maxsize=1)

class ProgressInfo:
    
    def __init__(self, scores=[], gen=0, last_backup=0, save_file=None):
        self.scores = scores
        self.gen = gen
        self.last_backup = last_backup
        self.save_file = save_file
    

def get_arg_parser():
    parser = argparse.ArgumentParser(
        description="Robogen execution script.",
        formatter_class=RawTextHelpFormatter)
    parser.add_argument("-l", "--load_file",
                        help="File containing a previously saved Generation.",
                        default=None)
    parser.add_argument("-s", "--save_file",
                        help="File to save last Generation to.",
                        default=constants.default_save)
    parser.add_argument("-g", "--gens", type=int,
                        help="Number of generations to run.",
                        default=1)
    parser.add_argument("-p", "--processes", type=int,
                        help="Number of worker processes allowed to run simultaneously.",
                        default=constants.default_cpu_count)
    return parser
    
def save_generation(generation, filename):
    if len(filename) <= 2 or filename[len(filename)-2: len(filename)] != ".p":
        filename = filename + ".p"
    try:
        pickle.dump(generation, open(filename, "wb"))
    except IOError:
        print "Could not save", filename
        sys.exit(1)
    
def load_generation(filename):
    if len(filename) <= 2 or filename[len(filename)-2: len(filename)] != ".p":
        filename = filename + ".p"
    try:
        generation = pickle.load(open(filename, "rb"))
        print "Resuming from", filename
        print "Last Generation Processed:", generation.num
        score_str = "Sorted Scores"
        for individual in generation.population:
            score_str = score_str + " : {0}".format(individual.score)
        print score_str
        return generation
    except IOError:
        print "Could not open", filename + ",", "returning new Generation"
        generation = Generation()
        generation.populate()
        return generation

def initial_score_individuals(args):

    individual = args[0]
    gen = args[1]
    options = rgrun.Options()
    options.headless = True
    options.quiet = 10
    options.n_of_games = constants.games_per_scoring
    individual.score = 0
    players = [Player(robot=individual.get_robot()), None]
    
    folder = os.getcwd()
    folder = os.path.join(folder, "rgkit", "bots")
    
    # AS PLAYER 1
    # Play against the coded bots
    for file_name in os.listdir(folder):
        loc_path = os.path.join("rgkit", "bots", file_name)
        #print "\t\tOpponent:", file_name
        try:
            players[1] = Player(file_name=loc_path)
        except IOError:
            print "Error opening", loc_path
            sys.exit(1)
        results = rgrun.Runner(players=players, options=options).run()
        individual.score += sum(p1 > p2 for p1, p2 in results)
        
    # Play against other elites in generation
    is_elite = (gen.population.index(individual) < constants.elite_size)
    if is_elite:
        individual.score += 1       # Free win for being in elite
        for elite_idx in range(constants.elite_size):
            if individual is not gen.population[elite_idx]:
                players[1] = Player(name="individual",
                                    robot=gen.population[elite_idx].get_robot())
                results = rgrun.Runner(players=players, options=options).run()
                individual.score += sum(p1 > p2 for p1, p2 in results)
    else:
        # No free win for non-elite contenders
        for elite_idx in range(constants.elite_size):
            players[1] = Player(name="individual",
                                robot=gen.population[elite_idx].get_robot())
            results = rgrun.Runner(players=players, options=options).run()
            individual.score += sum(p1 > p2 for p1, p2 in results)
            
    # AS PLAYER 2
    players = [None, Player(robot=individual.get_robot())]
    # Play against the coded bots
    for file_name in os.listdir(folder):
        loc_path = os.path.join("rgkit", "bots", file_name)
        #print "\t\tOpponent:", file_name
        try:
            players[0] = Player(file_name=loc_path)
        except IOError:
            print "Error opening", loc_path
            sys.exit(1)
        results = rgrun.Runner(players=players, options=options).run()
        individual.score += sum(p1 > p2 for p1, p2 in results)
        
    # Play against other elites in generation
    is_elite = (gen.population.index(individual) < constants.elite_size)
    if is_elite:
        individual.score += 1       # Free win for being in elite
        for elite_idx in range(constants.elite_size):
            if individual is not gen.population[elite_idx]:
                players[0] = Player(name="individual",
                                    robot=gen.population[elite_idx].get_robot())
                results = rgrun.Runner(players=players, options=options).run()
                individual.score += sum(p1 > p2 for p1, p2 in results)
    else:
        # No free win for non-elite contenders
        for elite_idx in range(constants.elite_size):
            players[0] = Player(name="individual",
                                robot=gen.population[elite_idx].get_robot())
            results = rgrun.Runner(players=players, options=options).run()
            individual.score += sum(p1 > p2 for p1, p2 in results)
        
    return individual.score
    
def break_ties(args):
    
    individual = args[0]
    tied_individuals = args[1]
    options = rgrun.Options()
    options.headless = True
    options.quiet = 10
    options.n_of_games = constants.games_per_scoring
    individual.score = 0
    players = [Player(robot=individual.get_robot()), None]
    
    # AS PLAYER 1
    # Play against other elites in generation
    for opponent in tied_individuals:
        if individual is not opponent:
            players[1] = Player(name="individual", robot=opponent.get_robot())
            results = rgrun.Runner(players=players, options=options).run()
            individual.score += sum(p1 > p2 for p1, p2 in results)
            
    # AS PLAYER 2
    players = [None, Player(robot=individual.get_robot())]
    # Play against other elites in generation
    for opponent in tied_individuals:
        if individual is not opponent:
            players[0] = Player(name="individual", robot=opponent.get_robot())
            results = rgrun.Runner(players=players, options=options).run()
            individual.score += sum(p1 > p2 for p1, p2 in results)
    
    return individual.score
        
def worker(args):

    # Init
    gen = None
    last_backup = 0
    if args.load_file is not None:
        gen = load_generation(args.load_file)
        last_backup = gen.num
        gen = gen.propagate()
    else:
        gen = Generation()
        gen.populate()
    save_file = args.save_file
    
    # For each generation
    for gen_num in range(1, args.gens+1):
    
        # INITIAL SCORING
        # Individual VS Elites and Coded Bots
        individual_pool = Pool(processes=args.processes)
        scores = individual_pool.map(initial_score_individuals, 
                                     [(x, gen) for x in gen.population])
        sorted_scores = []
        individual_pool.close()
        individual_pool.join()
        for x in range(len(gen.population)):
            gen.population[x].score = scores[x]
            sorted_scores.append(gen.population[x].score)
        sorted_scores.sort()
        sorted_scores.reverse()
        
        # ELITE SCORING AND SORTING
        # Break Ties that cross the ELITE/NON-ELITE cutoff
        num_elites = constants.elite_size
        if sorted_scores[num_elites-1] == sorted_scores[num_elites]:
            tie_score = sorted_scores[num_elites]
            tied_individuals = []
            for individual in gen.population:
                if individual.score == tie_score:
                    tied_individuals.append(individual)
            # Break The Ties
            individual_pool = Pool(processes=args.processes)
            finer_scores = individual_pool.map(break_ties, 
                               [(x, tied_individuals) for x in tied_individuals])
            individual_pool.close()
            individual_pool.join()
            # New scores are in range [tie_score, tie_score+1)
            for x in range(len(tied_individuals)):
                tied_individuals[x].score = ((tie_score * 2 * (len(tied_individuals)-1)) +
                        finer_scores[x]) / float(2 * (len(tied_individuals)-1))

            scores = []
            for x in range(len(gen.population)):
                scores.append(gen.population[x].score)
        gen.sort_by_score()
        
        # Clobber if necessary
        try:
            progress_q.get_nowait()
        except Queue.Empty:
            pass
        
        # If work is done or early stop is requested: save, inform, finish
        if gen_num == args.gens or not early_end_q.empty():
            progress_q.put(ProgressInfo(scores, gen.num, last_backup, save_file))
            save_generation(gen, save_file)
            break
        # Otherwise: inform and move to next generation
        else:
            if (gen_num % constants.backup_frequency) == (constants.backup_frequency-1):
                save_generation(gen, constants.default_backup)
                last_backup = gen.num
            progress_q.put(ProgressInfo(scores, gen.num, last_backup))
            gen = gen.propagate()
                        

def main():

    # Get args: load or new; number of generations; TODO: More options
    args = get_arg_parser().parse_args()
    
    clear()
    if args.load_file is not None:
        # The printout for this is in the load_generation method
        pass
    else:
        print "Starting evolution from scratch . . ."
        
    work_thread = threading.Thread(target=worker, args=(args,))
    work_thread.start()
    gen = 0
    scores = []
    progress = None
    
    # Status Printing Loop until work finished or SPACE pressed
    ended_naturally = False
    while not msvcrt.kbhit() or msvcrt.getch() != " ":
        # Each finished generation fills the progress_q
        try:
            progress = progress_q.get_nowait()
            if progress.save_file is not None:
                ended_naturally = True
                break
        except Queue.Empty:
            pass
        print_status(progress)
        time.sleep(1)
    # If SPACE was pressed, inform work thread through early_end_q
    if not ended_naturally:
        progress = ProgressInfo()
        clear()
        print "Gracefully exiting and saving progress.\nPlease wait",
        early_end_q.put(ProgressInfo(save_file=True))
        # Wait for work thread to save progress
        while progress.save_file is None:
            try:
                print ".",
                progress = progress_q.get_nowait()
                print ""  # Get rid of a left over space from the above printout
            except Queue.Empty:
                time.sleep(1)

    work_thread.join()
    print_status(progress)

    
spinner = 0
def print_status(progress):
    if progress is None:
        return
        
    clear()
    if progress.save_file is None:
        global spinner
        print "Processing Generations ",
        if spinner == 0:
            print "-"
        elif spinner == 1:
            print "\\"
        elif spinner == 2:
            print "|"
        elif spinner == 3:
            print "/"
        spinner = (spinner + 1) % 4
    else:
        print "Execution finished. Progress saved in", progress.save_file
    print "Last Generation Processed:", progress.gen,
    print "\tLast Backup Generation:", progress.last_backup
    max_score = (2.0 * constants.games_per_scoring * 
                 (constants.elite_size + constants.num_coded_opponents)) + 1.0
    scores = []
    score_str = "       Scores"
    for score in progress.scores:
        scores.append((score / max_score) * 100.0)
    for score in scores:
        score_str = score_str + " : {:.1f}".format(score)
    score_str = score_str + "\nSorted Scores"
    scores.sort()
    scores.reverse()
    for score in scores:
        score_str = score_str + " : {:.1f}".format(score)
    print score_str
    if progress.save_file is None:
        print "Press Spacebar to save progress and exit."
        
def clear():
    os.system('cls' if os.name == 'nt' else 'clear')
            

if __name__ == '__main__':
    main()
    