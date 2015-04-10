import time
import os
import random

from rgkit import run as rgrun
from rgkit.game import Player
from rgkit.gamestate import GameState

from individual import Individual
from rules import Node
import constants

class Test:
    """Test Suite for Individuals' behavior."""

    def __init__(self):
        self.clear_test_state()

    def test_eval_order(self):
        """Verifies that an Individual's Rule evaluation order is followed."""
        
        # Test Init
        print "-- Eval Order Test --"
        self.clear_test_state()
        self.robots.append(Individual().get_robot())
        testee = self.robots[0]
        self.gamestate.add_robot(testee.location, testee.player_id)
        for rule in testee.eval_order:
            rule.insert_random_parent()
            node = rule.root
            node.type = "HP"
            node.not_op = False
            node.hp = 25
            node.comp_op = "GT"
            
        # Test each rule with its preceding rules False and its succeeding rules True
        for rule in testee.eval_order:
            result = testee.act(self.gamestate.get_game_info(testee.player_id))
            if len(result) == 0:
                print "Test Failed: No action returned"
                return
            elif result[0] != rule.action:
                print "Test Failed: Expected Evaluation Order Incorrect"
                print "    Expected:", rule.action, "Actual:", result[0]
                return
            rule.root.comp_op = "LT"
            
        # Test default action
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: Default action should be 'guard'"
            return
            
        print "PASSED"

    def test_all_node_types(self):
        """Tests the evaluation logic for each Node type."""
        
        self.test_self_hp_node_type()
        self.test_spawn_timer_node_type()
        self.test_rloc_enemy_node_type()
        self.test_rloc_spawn_node_type()
        self.test_rloc_invalid_node_type()
        self.test_rloc_empty_node_type()
        self.test_rloc_ally_node_type()
        self.test_rloc_fut_ally_node_type()
        self.test_rloc_fut_attack_node_type()
        
    def init_node_type_test(self):
        """Puts Test in known state for Node type tests."""

        self.clear_test_state()
        player1 = Individual()
        player2 = Individual()
        testee = player1.get_robot()
        testee.location = constants.testee_loc
        ally = player1.get_robot()
        ally.location = constants.ally_loc
        enemy = player2.get_robot()
        enemy.location = constants.enemy_loc
        enemy.player_id = 1
        self.robots = [testee, ally, enemy]
        for bot in self.robots:
            self.gamestate.add_robot(bot.location, bot.player_id)
            
        # I use the default 'guard' action to determine when a rule evaluates 
        #     False, so the test rule must not be the guard rule
        while testee.eval_order[0].action == 'guard':
            random.shuffle(testee.eval_order)
        testee.eval_order[0].insert_random_parent()
        
    def test_self_hp_node_type(self):
        """Tests self HP Node evaluation logic."""
        
        print "-- Test Self HP Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "HP"
        node.not_op = False
        testee.hp = 25
        
        # Test LT
        node.comp_op = "LT"
        node.hp = 26
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on LT True subtest"
            return
        node.hp = 25
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on LT False subtest"
            return
            
        # Test GT
        node.comp_op = "GT"
        node.hp = 24
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on GT True subtest"
            return
        node.hp = 25
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on GT False subtest"
            return
            
        print "PASSED"
        
    def test_spawn_timer_node_type(self):
        """Tests spawn timer Node evaluation logic."""
        
        print "-- Test Spawn Timer Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "SPAWN"
        node.not_op = False
        self.gamestate.turn = 5
        
        # Test LT
        node.comp_op = "LT"
        node.turns_since_spawn = 6
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on LT True subtest"
            return
        node.turns_since_spawn = 5
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on LT False subtest"
            return
            
        # Test GT
        node.comp_op = "GT"
        node.turns_since_spawn = 4
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on GT True subtest"
            return
        node.turns_since_spawn = 5
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on GT False subtest"
            return
            
        print "PASSED"
        
    def test_rloc_enemy_node_type(self):
        """Tests relative enemy location Node evaluation logic."""
        
        print "-- Test RLOC Enemy Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        ally = self.robots[1]
        enemy = self.robots[2]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "ENEMY"
        node.not_op = False
        node.hp = 0
        node.comp_op = "GT"
        
        # Test Location
        node.rloc = (ally.location[0] - testee.location[0],
                     ally.location[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Location False subtest"
            return
        node.rloc = (enemy.location[0] - testee.location[0], 
                     enemy.location[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on Location True subtest"
            return
        
        # Test HP LT
        node.comp_op = "LT"
        node.hp = 25
        self.gamestate.robots[enemy.location].hp = 24
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on HP LT True subtest"
            return
        self.gamestate.robots[enemy.location].hp = 25
        self.gamestate.robots[ally.location].hp = 24
        self.gamestate.robots[testee.location].hp = 24
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on HP LT False subtest"
            return
            
        # Test HP GT
        node.comp_op = "GT"
        self.gamestate.robots[enemy.location].hp = 26
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on HP GT True subtest"
            return
        self.gamestate.robots[enemy.location].hp = 25
        self.gamestate.robots[ally.location].hp = 26
        self.gamestate.robots[testee.location].hp = 26
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on HP GT False subtest"
            return
        
        print "PASSED"

    def test_rloc_spawn_node_type(self):
        """Tests relative spawn location Node evaluation logic."""
        
        print "-- Test RLOC Spawn Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "SPAWN"
        node.not_op = False
        
        node.rloc = (constants.spawn_square[0] - testee.location[0],
                     constants.spawn_square[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on Spawn Location True subtest"
            return
        node.rloc = (0,0)
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Spawn Location False subtest"
            return
            
        print "PASSED"
        
    def test_rloc_invalid_node_type(self):
        """Tests relative location validity Node evaluation logic."""
        
        print "-- Test RLOC Invalid Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "INVALID"
        node.not_op = False
        
        # Test True: Obstacle and Invalid
        node.rloc = (constants.obstacle_square[0] - testee.location[0],
                     constants.obstacle_square[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on Invalid True (Obstacle) subtest"
            return
        node.rloc = (constants.invalid_square[0] - testee.location[0],
                     constants.invalid_square[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on Invalid True (Invalid) subtest"
            return
            
        # Test False
        node.rloc = (0,0)
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Invalid False subtest"
            return
            
        print "PASSED"
        
    def test_rloc_empty_node_type(self):
        """Tests relative location emptiness Node evaluation logic."""
        
        print "-- Test RLOC Empty Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        ally = self.robots[1]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "EMPTY"
        node.not_op = False
        
        # Test False: Obstacle, Invalid, Other, Self
        node.rloc = (constants.obstacle_square[0] - testee.location[0],
                     constants.obstacle_square[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Empty False (Obstacle) subtest"
            return
        node.rloc = (constants.invalid_square[0] - testee.location[0],
                     constants.invalid_square[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Empty False (Invalid) subtest"
            return
        node.rloc = (ally.location[0] - testee.location[0],
                     ally.location[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Empty False (Ally) subtest"
            return
        node.rloc = (0,0)
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Empty False (Self) subtest"
            return
        
        # Test True
        node.rloc = (constants.empty_square[0] - testee.location[0],
                     constants.empty_square[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on Empty True subtest"
            return
            
        print "PASSED"
        
    def test_rloc_ally_node_type(self):
        """Tests relative ally location Node evaluation logic."""
        
        print "-- Test RLOC Ally Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        ally = self.robots[1]
        enemy = self.robots[2]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "ALLY"
        node.not_op = False
        node.hp = 0
        node.comp_op = "GT"
        
        # Test Location
        node.rloc = (enemy.location[0] - testee.location[0],
                     enemy.location[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on Location False subtest"
            return
        node.rloc = (ally.location[0] - testee.location[0], 
                     ally.location[1] - testee.location[1])
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on Location True subtest"
            return
        
        # Test HP LT
        node.comp_op = "LT"
        node.hp = 25
        self.gamestate.robots[ally.location].hp = 24
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on HP LT True subtest"
            return
        self.gamestate.robots[ally.location].hp = 25
        self.gamestate.robots[enemy.location].hp = 24
        self.gamestate.robots[testee.location].hp = 24
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on HP LT False subtest"
            return
            
        # Test HP GT
        node.comp_op = "GT"
        self.gamestate.robots[ally.location].hp = 26
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on HP GT True subtest"
            return
        self.gamestate.robots[ally.location].hp = 25
        self.gamestate.robots[enemy.location].hp = 26
        self.gamestate.robots[testee.location].hp = 26
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on HP GT False subtest"
            return
        
        print "PASSED"
        
    def test_rloc_fut_ally_node_type(self):
        """Tests relative future ally location Node evaluation logic."""
        
        print "-- Test RLOC Future Ally Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        ally = self.robots[1]
        enemy = self.robots[2]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "ALLY_FUT"
        node.not_op = False
        node.hp = 0
        node.comp_op = "GT"
        node.rloc = (constants.testee_left[0] - testee.location[0],
                     constants.testee_left[1] - testee.location[1])
        
        # Test True
        ally_move = ally.move_rule
        ally_move.insert_random_parent()
        ally_node = ally_move.root
        ally_node.direction = "UP"
        ally_node.type = "HP"
        ally_node.not_op = False
        ally_node.hp = 0
        ally_node.comp_op = "GT"
        ally.act(self.gamestate.get_game_info(ally.player_id))
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on True subtest"
            return
            
        # Test False: Next turn should reset future_moves array
        self.gamestate.turn = self.gamestate.turn + 1
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on False (future_moves array reset) subtest"
            return
        
        # Test False: True if enemy counts
        enemy_move = enemy.move_rule
        enemy_move.insert_random_parent()
        enemy_node = enemy_move.root
        enemy_node.direction = "DOWN"
        enemy_node.type = "HP"
        enemy_node.not_op = False
        enemy_node.hp = 0
        enemy_node.comp_op = "GT"
        enemy.act(self.gamestate.get_game_info(enemy.player_id))
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on False (enemy moves shouldn't count) subtest"
            return
            
        print "PASSED"
        
    def test_rloc_fut_attack_node_type(self):
        """Tests relative future attack location Node evaluation logic."""
        
        print "-- Test RLOC Future Attack Node Type --"
        self.init_node_type_test()
        testee = self.robots[0]
        ally = self.robots[1]
        enemy = self.robots[2]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "RLOC"
        node.rloc_type = "ATT_FUT"
        node.not_op = False
        node.hp = 0
        node.comp_op = "GT"
        node.rloc = (constants.testee_left[0] - testee.location[0],
                     constants.testee_left[1] - testee.location[1])
        
        # Test True
        ally_attack = ally.attack_rule
        ally_attack.insert_random_parent()
        ally_node = ally_attack.root
        ally_node.direction = "UP"
        ally_node.type = "HP"
        ally_node.not_op = False
        ally_node.hp = 0
        ally_node.comp_op = "GT"
        ally.act(self.gamestate.get_game_info(ally.player_id))
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on True subtest"
            return
            
        # Test False: Next turn should reset future_attacks array
        self.gamestate.turn = self.gamestate.turn + 1
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on False (future_attacks array reset) subtest"
            return
        
        # Test False: True if enemy counts
        enemy_attack = enemy.attack_rule
        enemy_attack.insert_random_parent()
        enemy_node = enemy_attack.root
        enemy_node.direction = "DOWN"
        enemy_node.type = "HP"
        enemy_node.not_op = False
        enemy_node.hp = 0
        enemy_node.comp_op = "GT"
        enemy.act(self.gamestate.get_game_info(enemy.player_id))
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on False (enemy attacks shouldn't count) subtest"
            return
            
        print "PASSED"
        
    def test_not_op(self):
        """Tests the NOT op for a Node.
        
        The evaluation of the NOT op comes after all other Node logic (not
        including children) and therefore a single test will suffice.
        """
        
        print "-- Test NOT op --"
        self.init_node_type_test()
        testee = self.robots[0]
        action = testee.eval_order[0].action
        node = testee.eval_order[0].root
        node.type = "HP"
        node.hp = 0
        node.comp_op = "GT"
        
        node.not_op = False
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != action:
            print "Test Failed: on True subtest"
            return
        node.not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on False subtest"
            return
            
        print "PASSED"
        
    def test_children(self):
        """Tests evaluation logic for a Node with children.
        
        This will consider different combinations of AND and OR children Nodes.
        Based on their evaluation, the action and/or direction should change.
        """
        
        print "-- Test Children Logic --"
        directions = ["UP", "DOWN", "LEFT", "RIGHT"]
        dir_idx = 0
        
        # Test T root with T-T-T AND children
        num_children = 3
        self.init_children_test(num_children)
        testee = self.robots[0]
        action = testee.eval_order[0].action
        root = testee.eval_order[0].root
        
        root.type = "HP"
        root.hp = 0
        root.not_op = False
        root.comp_op = "GT"
        root.direction = directions[dir_idx]
        dir_idx += 1
        for x in range(num_children):
            node = root.children[x]
            node.op = "AND"
            node.type = "HP"
            node.hp = 0
            node.not_op = False
            node.comp_op = "GT"
            node.direction = directions[dir_idx]
            dir_idx = (dir_idx + 1) % len(directions)
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) < 2 or result[0] != action or result[1] != constants.testee_right:
            print "Test Failed: on T root with T AND children"
            return
            
        # Test F root with T-T-T AND children
        root.not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on F root with T AND children"
            return

        # Test T root with T-F-T AND children
        root.not_op = False
        root.children[1].not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on T root with T-F-T AND children"
            return

        # Test T root with F-T-T OR children (middle determines direction)
        root.op = "OR"
        for x in range(num_children):
            node = root.children[x]
            node.op = "OR"
            node.not_op = False
        root.children[0].not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) < 2 or result[0] != action or result[1] != constants.testee_left:
            print "Test Failed: on T root with F-T-T OR children"
            return
        
        # Test F root with T-F-T OR children
        root.not_op = True
        root.children[0].not_op = False
        root.children[1].not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) < 2 or result[0] != action or result[1] != constants.testee_down:
            print "Test Failed: on F root with T-F-T OR children"
            return
        
        # Test T root with F-F-F OR children
        root.not_op = False
        root.children[0].not_op = True
        root.children[2].not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) < 2 or result[0] != action or result[1] != constants.testee_up:
            print "Test Failed: on T root with F OR children"
            return
        
        # Test F root with F-F-F OR children
        root.not_op = True
        root.children[1].not_op = True
        result = testee.act(self.gamestate.get_game_info(testee.player_id))
        if len(result) == 0 or result[0] != 'guard':
            print "Test Failed: on F root with F OR children"
            return
        
        print "PASSED"
        
    def init_children_test(self, num_children):

        self.clear_test_state()
        player1 = Individual()
        testee = player1.get_robot()
        testee.location = constants.testee_loc
        self.robots = [testee]
        self.gamestate.add_robot(testee.location, testee.player_id)
        
        # Force the prime rule to be the move rule so direction is returned
        while testee.eval_order[0].action != 'move':
            random.shuffle(testee.eval_order)
        
        rule = self.robots[0].eval_order[0]
        rule.insert_random_parent()
        for x in range(num_children):
            self.insert_random_root_child(rule)

    def clear_test_state(self):
    
        runner = rgrun.Runner()
        self.gamestate = GameState()
        self.robots = []
        
    def insert_random_root_child(self, rule):
        
        node = rule.root
        new_node = Node.new_random_node()
        node.insert_child_randomly(new_node)
        new_node.parent = node
        rule.node_list.append(new_node)

        
def main():
    """Runs the full test suite."""
    
    test = Test()
    test.test_eval_order()
    test.test_all_node_types()
    test.test_not_op()
    test.test_children()

    
if __name__ == '__main__':
    main()
