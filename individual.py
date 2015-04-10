import random

import rules

class Individual:
    """This class defines an individual robot's behavior."""

    mut_types = ("INS_PAR", "INS_CHI", "DEL_NOD", "DEL_BRA", "FLP_OP",
                 "FLP_NOP", "SWP_NOD", "SWP_BRA", "CHG_DIR", "CHI_ORD",
                 "EVL_ORD")

    def __init__(self):
        
        self.score = 0
        self.gens_as_elite = 0
        self.move_rule = rules.Rule('move')
        self.attack_rule = rules.Rule('attack')
        self.guard_rule = rules.Rule('guard')
        self.suicide_rule = rules.Rule('suicide')
        self.eval_order = [self.move_rule, self.attack_rule, 
                           self.guard_rule, self.suicide_rule]
        random.shuffle(self.eval_order)
        
        self.location = (9, 9)
        self.player_id = 0
        self.hp = 50
        self.robot_id = 0
        
        self.future_moves = []
        self.future_attacks = []
        self.future_moves_turn = -1
        
    def get_robot(self):
        """Creates Robot that behaves according to this Individual's rules."""
        
        return Robot(self)
        
    def make_copy(self):
        """Creates a deep copy of this Individual."""
        
        result = Individual()
        
        result.move_rule = self.move_rule.make_copy()
        result.attack_rule = self.attack_rule.make_copy()
        result.guard_rule = self.guard_rule.make_copy()
        result.suicide_rule = self.suicide_rule.make_copy()
        
        idx = self.eval_order.index(self.move_rule)
        result.eval_order[idx] = result.move_rule
        idx = self.eval_order.index(self.attack_rule)
        result.eval_order[idx] = result.attack_rule
        idx = self.eval_order.index(self.guard_rule)
        result.eval_order[idx] = result.guard_rule
        idx = self.eval_order.index(self.suicide_rule)
        result.eval_order[idx] = result.suicide_rule
        
        return result
        
    @staticmethod
    def cross(one, other):
        """Creates a cross of two Individuals."""
        
        first = one.make_copy()
        second = other.make_copy()
        swap_nodes = (random.random() < 0.5)
        swap_branches = (random.random() < 0.5)
        swap_rule = (random.random() < 0.5)
        swap_order = (random.random() < 0.5)
        if swap_nodes:
            Individual.swap_nodes(first, second)
        if swap_branches:
            Individual.swap_branches(first, second)
        if swap_rule:
            Individual.swap_rules(first, second)
        if swap_order:
            Individual.swap_order(first, second)
        return first
        
    @staticmethod
    def swap_nodes(first, second):
        """Swaps two random nodes of given Individuals."""
    
        # Pick the Rules (Think of them as chromosomes)
        choice = random.choice(["MOVE", "ATTACK", "GUARD", "SUICIDE"])
        rule1 = None
        rule2 = None
        if choice == "MOVE":
            rule1 = first.move_rule
            rule2 = second.move_rule
        elif choice == "ATTACK":
            rule1 = first.attack_rule
            rule2 = second.attack_rule
        elif choice == "GUARD":
            rule1 = first.guard_rule
            rule2 = second.guard_rule
        elif choice == "SUICIDE":
            rule1 = first.suicide_rule
            rule2 = second.suicide_rule
            
        # Handle empty rules by creating a single node
        if not len(rule1.node_list):
            rule1.insert_random_parent()
        if not len(rule2.node_list):
            rule2.insert_random_parent()
            
        # Pick the nodes
        idx = random.randrange(len(rule1.node_list))
        nd1 = rule1.node_list[idx]
        idx = random.randrange(len(rule2.node_list))
        nd2 = rule2.node_list[idx]
            
        # Swap Parents and Adjust Parents' children lists
        if nd1.is_root() and nd2.is_root():
            rule1.root = nd2
            rule2.root = nd1
        elif nd1.is_root():
            rule1.root = nd2
            nd1.root = False
            nd2.root = True
            nd1.parent = nd2.parent
            idx_as_child2 = nd2.parent.children.index(nd2)
            nd2.parent.children.remove(nd2)
            nd1.parent.children.insert(idx_as_child2, nd1)
            nd2.parent = None
        elif nd2.is_root():
            rule2.root = nd1
            nd2.root = False
            nd1.root = True
            nd2.parent = nd1.parent
            idx_as_child1 = nd1.parent.children.index(nd1)
            nd1.parent.children.remove(nd1)
            nd2.parent.children.insert(idx_as_child1, nd2)
            nd1.parent = None
        else:
            idx_as_child1 = nd1.parent.children.index(nd1)
            idx_as_child2 = nd2.parent.children.index(nd2)
            nd1.parent.children.remove(nd1)
            nd2.parent.children.remove(nd2)
            nd1.parent.children.insert(idx_as_child1, nd2)
            nd2.parent.children.insert(idx_as_child2, nd1)
            temp = nd1.parent
            nd1.parent = nd2.parent
            nd2.parent = temp
            
        # Swap Children
        temp = nd1.children
        nd1.children = nd2.children
        nd2.children = temp
        if len(nd1.children):
            for child in nd1.children:
                child.parent = nd1
        if len(nd2.children):
            for child in nd2.children:
                child.parent = nd2
        
        # Swap node_list membership
        rule1.node_list.remove(nd1)
        rule2.node_list.remove(nd2)
        rule1.node_list.append(nd2)
        rule2.node_list.append(nd1)

    @staticmethod
    def swap_branches(first, second):
        """Swap two random branches of given Individuals."""
    
        # Pick the Rules (Think of them as chromosomes)
        choice = random.choice(["MOVE", "ATTACK", "GUARD", "SUICIDE"])
        rule1 = None
        rule2 = None
        if choice == "MOVE":
            rule1 = first.move_rule
            rule2 = second.move_rule
        elif choice == "ATTACK":
            rule1 = first.attack_rule
            rule2 = second.attack_rule
        elif choice == "GUARD":
            rule1 = first.guard_rule
            rule2 = second.guard_rule
        elif choice == "SUICIDE":
            rule1 = first.suicide_rule
            rule2 = second.suicide_rule
            
        # Handle empty rules by creating a single node
        if not len(rule1.node_list):
            rule1.insert_random_parent()
        if not len(rule2.node_list):
            rule2.insert_random_parent()
            
        # Pick the branches
        idx = random.randrange(len(rule1.node_list))
        br1 = rule1.node_list[idx]
        idx = random.randrange(len(rule2.node_list))
        br2 = rule2.node_list[idx]
        
        # Swap Parents and Adjust Parents' children lists
        if br1.is_root() and br2.is_root():
            rule1.root = br2
            rule2.root = br1
        elif br1.is_root():
            rule1.root = br2
            br1.root = False
            br2.root = True
            br1.parent = br2.parent
            idx_as_child2 = br2.parent.children.index(br2)
            br2.parent.children.remove(br2)
            br1.parent.children.insert(idx_as_child2, br1)
            br2.parent = None
        elif br2.is_root():
            rule2.root = br1
            br2.root = False
            br1.root = True
            br2.parent = br1.parent
            idx_as_child1 = br1.parent.children.index(br1)
            br1.parent.children.remove(br1)
            br2.parent.children.insert(idx_as_child1, br2)
            br1.parent = None
        else:
            idx_as_child1 = br1.parent.children.index(br1)
            idx_as_child2 = br2.parent.children.index(br2)
            br1.parent.children.remove(br1)
            br2.parent.children.remove(br2)
            br1.parent.children.insert(idx_as_child1, br2)
            br2.parent.children.insert(idx_as_child2, br1)
            temp = br1.parent
            br1.parent = br2.parent
            br2.parent = temp
        
        # Swap node_list membership
        rule1.delete_branch_at(br1)
        rule2.delete_branch_at(br2)
        rule1.add_branch_at(br2)
        rule2.add_branch_at(br1)
        
        return
        
    @staticmethod
    def swap_rules(first, second):
        """Swap random set of rules for given Individuals."""
        
        choice = random.choice(["MOVE", "ATTACK", "GUARD", "SUICIDE"])
        if choice == "MOVE":
            temp = first.move_rule
            first.move_rule = second.move_rule
            second.move_rule = temp
            first.eval_order[first.eval_order.index(second.move_rule)] = first.move_rule
            second.eval_order[second.eval_order.index(first.move_rule)] = second.move_rule
        elif choice == "ATTACK":
            temp = first.attack_rule
            first.attack_rule = second.attack_rule
            second.attack_rule = temp
            first.eval_order[first.eval_order.index(second.attack_rule)] = first.attack_rule
            second.eval_order[second.eval_order.index(first.attack_rule)] = second.attack_rule
        elif choice == "GUARD":
            temp = first.guard_rule
            first.guard_rule = second.guard_rule
            second.guard_rule = temp
            first.eval_order[first.eval_order.index(second.guard_rule)] = first.guard_rule
            second.eval_order[second.eval_order.index(first.guard_rule)] = second.guard_rule
        elif choice == "SUICIDE":
            temp = first.suicide_rule
            first.suicide_rule = second.suicide_rule
            second.suicide_rule = temp
            first.eval_order[first.eval_order.index(second.suicide_rule)] = first.suicide_rule
            second.eval_order[second.eval_order.index(first.suicide_rule)] = second.suicide_rule
    
    @staticmethod
    def swap_order(first, second):
        """Swap Rule orders for given Individuals."""
        
        idx1m = first.eval_order.index(first.move_rule)
        idx2m = second.eval_order.index(second.move_rule)
        idx1a = first.eval_order.index(first.attack_rule)
        idx2a = second.eval_order.index(second.attack_rule)
        idx1g = first.eval_order.index(first.guard_rule)
        idx2g = second.eval_order.index(second.guard_rule)
        idx1s = first.eval_order.index(first.suicide_rule)
        idx2s = second.eval_order.index(second.suicide_rule)
        first.eval_order[idx2m] = first.move_rule
        first.eval_order[idx2a] = first.attack_rule
        first.eval_order[idx2g] = first.guard_rule
        first.eval_order[idx2s] = first.suicide_rule
        second.eval_order[idx1m] = second.move_rule
        second.eval_order[idx1a] = second.attack_rule
        second.eval_order[idx1g] = second.guard_rule
        second.eval_order[idx1s] = second.suicide_rule
        
    def do_mutations(self, num_muts):
        """Creates a mutated clone of Individual."""
        
        result = self.make_copy()
        
        for num in range(num_muts):
            result.mutate()
            
        return result
            
    def mutate(self):
        """Perform a random mutation on Individual."""
        
        type = random.choice(Individual.mut_types)
        if type == "EVL_ORD":
            random.shuffle(self.eval_order)
        else:
            rule = random.choice(self.eval_order)
            if type == "INS_PAR":
                rule.insert_random_parent()
            elif type == "INS_CHI":
                rule.insert_random_child()
            elif type == "DEL_NOD":
                rule.delete_random_node()
            elif type == "DEL_BRA":
                rule.delete_random_branch()
            elif type == "FLP_OP":
                rule.flip_random_op()
            elif type == "FLP_NOP":
                rule.flip_random_not_op()
            elif type == "SWP_NOD":
                rule.swap_random_nodes()
            elif type == "SWP_BRA":
                rule.swap_random_branches()
            elif type == "CHG_DIR":
                rule.change_random_direction()
            elif type == "CHI_ORD":
                rule.jumble_random_child_order()
            
    def __lt__(self, other):
        return ((self.score < other.score) or 
                ((self.score == other.score) and 
                (self.gens_as_elite < other.gens_as_elite)))
            
    def debug_print(self):
        print "INDIVIDUAL"
        print "Score:", self.score, "Gens as Elite:", self.gens_as_elite
        print "Move Rule - Eval Order:", (self.eval_order.index(self.move_rule)+1)
        self.move_rule.debug_print()
        print "Attack Rule - Eval Order:", (self.eval_order.index(self.attack_rule)+1)
        self.attack_rule.debug_print()
        print "Guard Rule - Eval Order:", (self.eval_order.index(self.guard_rule)+1)
        self.guard_rule.debug_print()
        print "Suicide Rule - Eval Order:", (self.eval_order.index(self.suicide_rule)+1)
        self.suicide_rule.debug_print()
        print " "
        
class Robot(Individual):
    """This class defines a single Robot based on the given Individual's rules."""

    def __init__(self, individual):
        self.location = (9, 9)
        self.player_id = 0
        self.hp = 50
        self.robot_id = 0
        
        self.parent = individual
        self.move_rule = individual.move_rule
        self.attack_rule = individual.attack_rule
        self.guard_rule = individual.guard_rule
        self.suicide_rule = individual.suicide_rule
        self.eval_order = individual.eval_order

    def act(self, game):
        """Called by Robot Game. Returns a Robot's behavior given a game state."""
    
        action = []
        
        # Reset decision-sharing fields at start of each turn
        if game['turn'] != self.parent.future_moves_turn:
            self.parent.future_moves = [[0]*19 for i in range(19)]
            self.parent.future_attacks = [[0]*19 for i in range(19)]
            self.parent.future_moves_turn = game['turn']
        
        # Evaluate rules given the game state
        for rule in self.parent.eval_order:
            result = rule.evaluate(game, self, self.parent.future_moves,
                                   self.parent.future_attacks)
            
            if result[0]:
                for x in range(1, len(result)):
                    action.append(result[x])
                break
        if len(action) == 0:
            action.append('guard')
            
        # Set directions if needed and inform decision-sharing fields
        if action[0] == 'move':
            dest = action[1]
            self.parent.future_moves[dest[0]][dest[1]] = self.hp
        elif action[0] == 'attack':
            dest = action[1]
            self.parent.future_attacks[dest[0]][dest[1]] = True
            self.parent.future_moves[self.location[0]][self.location[1]] = self.hp
        else:
            self.parent.future_moves[self.location[0]][self.location[1]] = self.hp
            
        return action
        
    def debug_print(self):
        self.parent.debug_print()
            