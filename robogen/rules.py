import random

from rgkit import rg

import constants

class Rule:

    def __init__(self, arg_action):
        self.action = arg_action
        self.root = None
        self.node_list = []
        
    def make_copy(self):
        """Creates a deep copy of this Rule."""
        
        result = Rule(self.action)
        self.recursive_node_copy(self.root, None, result)
        return result
        
    @staticmethod
    def recursive_node_copy(node, other_parent, other_rule):
        """Recursively copies a Node tree."""
        
        node_copy = None
        if node is not None:
            node_copy = node.make_copy()
            other_rule.node_list.append(node_copy)
            node_copy.parent = other_parent
            if node.is_root():
                other_rule.root = node_copy
            for child in node.children:
                child_copy = Rule.recursive_node_copy(child, node_copy, other_rule)
                if child_copy is not None:
                    node_copy.children.append(child_copy)
        return node_copy
        
    def insert_random_parent(self):
        """Creates a parent Node for a random Node.
        
        Creates a root Node if Rule is empty."""
        
        if self.root is None:
            self.root = Node.new_random_node(True)
            self.node_list.append(self.root)
        else:
            idx = random.randint(0, (len(self.node_list) - 1))
            node = self.node_list[idx]
            if node.is_root():
                self.root = Node.new_random_node(True)
                node.parent = self.root
                node.root = False
                self.root.children.append(node)
                self.node_list.append(self.root)
            else:
                new_node = Node.new_random_node()
                new_node.parent = node.parent
                idx_as_child = node.parent.children.index(node)
                node.parent.children[idx_as_child] = new_node
                new_node.children.append(node)
                node.parent = new_node
                self.node_list.append(new_node)
        
    def insert_random_child(self):
        """Creates a child Node for a random Node.
        
        Creates a root Node if Rule is empty."""
        
        if self.root is None:
            self.root = Node.new_random_node(True)
            self.node_list.append(self.root)
        else:
            idx = random.randint(0, (len(self.node_list) - 1))
            node = self.node_list[idx]
            new_node = Node.new_random_node()
            node.insert_child_randomly(new_node)
            new_node.parent = node
            self.node_list.append(new_node)
    
    def delete_random_node(self):
        """Deletes a random Node."""
                
        if not len(self.node_list):
            return
            
        idx = random.randint(0, (len(self.node_list) - 1))
        node = self.node_list[idx]
                
        # Root
        if node.is_root():
            # No children = delete all
            if len(node.children) == 0:
                self.node_list.remove(node)
                self.root = None
            # One child = make child root
            elif len(node.children) == 1:
                child = node.children[0]
                self.node_list.remove(node)
                self.root = child
                child.parent = None
                child.root = True
            # Multiple children = make first child root
            else:
                first_child = node.children[0]
                first_child.parent = None
                first_child.root = True
                self.node_list.remove(node)
                self.root = first_child
                for idx in range(1, len(node.children)):
                    child = node.children[idx]
                    child.parent = first_child
                    first_child.insert_child_randomly(child)
        # Not root = shift children up
        else:
            par = node.parent
            par.children.remove(node)
            self.node_list.remove(node)
            for child in node.children:
                par.insert_child_randomly(child)
                child.parent = par
        
    def delete_random_branch(self):
        """Delete a random branch of Nodes."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node = self.node_list[idx]
        if node.is_root():
            self.root = None
        else:
            node.parent.children.remove(node)
        self.delete_branch_at(node)
        
    def delete_branch_at(self, node):
        """Recursively remove branch from node_list."""
        
        if not len(self.node_list):
            return
        self.node_list.remove(node)
        for child in node.children:
            self.delete_branch_at(child)
            
    def add_branch_at(self, node):
        """Recursively add branch to node_list."""
        
        self.node_list.append(node)
        for child in node.children:
            self.add_branch_at(child)
        
    def flip_random_op(self):
        """Flip the logical operator of a random Node."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node = self.node_list[idx]
        if node.op == "AND":
            node.op = "OR"
        else:
            node.op = "AND"
                
    def flip_random_not_op(self):
        """Flip the NOT operator of a random node."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node = self.node_list[idx]
        node.not_op = not node.not_op
        
    def swap_random_nodes(self):
        """Swap two random nodes."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node1 = self.node_list[idx]
        idx = random.randint(0, (len(self.node_list) - 1))
        node2 = self.node_list[idx]
        if node1 is not node2:
            # Swap Parent's children lists
            if node1.is_root():
                idx_as_child = node2.parent.children.index(node2)
                node2.parent.children.remove(node2)
                node2.parent.children.insert(idx_as_child, node1)
                self.root = node2
                node1.root = False
                node2.root = True
            elif node2.is_root():
                idx_as_child = node1.parent.children.index(node1)
                node1.parent.children.remove(node1)
                node1.parent.children.insert(idx_as_child, node2)
                self.root = node1
                node2.root = False
                node1.root = True
            else:
                idx_as_child = node2.parent.children.index(node2)
                node2.parent.children.remove(node2)
                node2.parent.children.insert(idx_as_child, node1)
                idx_as_child = node1.parent.children.index(node1)
                node1.parent.children.remove(node1)
                node1.parent.children.insert(idx_as_child, node2)
            # Swap Parents
            if node1 is node2.parent:
                node2.parent = node1.parent
                node1.parent = node2
            elif node2 is node1.parent:
                node1.parent = node2.parent
                node2.parent = node1
            else:
                temp = node1.parent
                node1.parent = node2.parent
                node2.parent = temp
            # Swap Children
            temp = node1.children
            node1.children = node2.children
            node2.children = temp
            for child in node1.children:
                child.parent = node1
            for child in node2.children:
                child.parent = node2
        
    def swap_random_branches(self):
        """Swap two random branches."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node1 = self.node_list[idx]
        idx = random.randint(0, (len(self.node_list) - 1))
        node2 = self.node_list[idx]
        # Branches must be entirely independent (also precludes root Node)
        if (not self.node_precedes_other(node1, node2)
                and not self.node_precedes_other(node2, node1)):
            # Swap Parents' children lists
            idx_as_child = node1.parent.children.index(node1)
            node1.parent.children.remove(node1)
            node1.parent.children.insert(idx_as_child, node2)
            idx_as_child = node2.parent.children.index(node2)
            node2.parent.children.remove(node2)
            node2.parent.children.insert(idx_as_child, node1)
            # Swap Parents
            temp = node1.parent
            node1.parent = node2.parent
            node2.parent = temp
        
    def node_precedes_other(self, node, other):
        """Check if Node is an ancestor of other Node."""
        
        if node is other:
            return True
        for child in node.children:
            if self.node_precedes_other(child, other):
                return True
        return False
        
    def change_random_direction(self):
        """Changes direction of random Node."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node = self.node_list[idx]
        node.direction = random.choice(Node.directions)
        
    def jumble_random_child_order(self):
        """Shuffle child order of random Node."""
        
        if not len(self.node_list):
            return
        idx = random.randint(0, (len(self.node_list) - 1))
        node = self.node_list[idx]
        random.shuffle(node.children)
            
    @staticmethod
    def gen_rloc_gaussian():
        """Creates random RLOC. Favors smaller numbers."""
        x = int(random.gauss(0, constants.rloc_gauss_sigma))
        if x > constants.rloc_max_step:
            x = constants.rloc_max_step
        elif x < -constants.rloc_max_step:
            x = -constants.rloc_max_step
        y = int(random.gauss(0, constants.rloc_gauss_sigma))
        if y > constants.rloc_max_step:
            y = constants.rloc_max_step
        elif y < -constants.rloc_max_step:
            y = -constants.rloc_max_step
        return (x, y)
        
    def debug_print(self):
        print "Root:", self.root
        if self.root is not None:
            self.root.debug_print()
        
    def evaluate(self, game, robot, ally_fut, attack_fut):
        """Evaluates this Rule given game state and shared-decision fields."""
        
        if self.root is None:
            return [False, 'guard']
        act = self.root.evaluate(game, robot, ally_fut, attack_fut)
        result = [act[0], self.action]
        if self.action == 'move' or self.action == 'attack':
            if act[1] == "UP":
                result.append((robot.location[0], robot.location[1] + 1))
            elif act[1] == "DOWN":
                result.append((robot.location[0], robot.location[1] - 1))
            elif act[1] == "LEFT":
                result.append((robot.location[0] - 1, robot.location[1]))
            else:
                result.append((robot.location[0] + 1, robot.location[1]))
        return result
    
        
class Node:
    """This defines a Node in the Rule decision tree."""

    arg_types = ("RLOC", "SPAWN", "HP")
    comp_ops = ("LT", "GT")
    operation_types = ("AND", "OR")
    rloc_types = ("ENEMY", "SPAWN", "INVALID", "EMPTY", "ALLY", "ALLY_FUT", "ATT_FUT")
    directions = ("UP", "DOWN", "RIGHT", "LEFT")
    rloc_w_hp = ("ENEMY", "ALLY", "ALLY_FUT")

    def __init__(self, operation, arg_type, par=None, arg_hp=0, arg_comp_op="LT",
                 arg_spawn=0, arg_rloc_type="EMPTY", arg_rloc=(0,0), arg_dir=None,
                 arg_not=False, arg_root=False):
                 
        self.type = arg_type
        self.root = arg_root
        self.op = operation
        self.parent = par
        self.children = []
        self.direction = arg_dir
        self.not_op = arg_not
        self.rloc_type = arg_rloc_type
        self.rloc = arg_rloc
        self.hp = arg_hp
        self.comp_op = arg_comp_op
        self.turns_since_spawn = arg_spawn
                
    @staticmethod
    def new_random_node(root=False):
        """Creates a random Node."""
        
        hp = 0
        comp_op = ""
        spawn = 0
        rloc = (0, 0)
        rloc_type = "EMPTY"
        dir = random.choice(Node.directions)
        not_op = (random.random() < 0.5)
        op = random.choice(Node.operation_types)
        type = random.choice(Node.arg_types)
        if type == "RLOC":
            rloc = Rule.gen_rloc_gaussian()
            rloc_type = random.choice(Node.rloc_types)
            if any(rloc_type == s for s in Node.rloc_w_hp):
                hp = random.randint(1, 50)
                comp_op = random.choice(Node.comp_ops)
        elif type == "SPAWN":
            spawn = random.randint(0, 9)
            comp_op = random.choice(Node.comp_ops)
        elif type == "HP":
            hp = random.randint(1, 50)
            comp_op = random.choice(Node.comp_ops)
        return Node(op, type, None, hp, comp_op, spawn, rloc_type, rloc, dir, not_op, root)
        
    def insert_child_randomly(self, child):
        """Inserts the child at random in this Node's children list."""
        
        last_idx = len(self.children) - 1
        if last_idx < 0:
            self.children.append(child)
        else:
            self.children.insert((random.randint(0, (len(self.children) - 1))), child)
        
    def remove_child(self, child):
        """Removes the child from this Node's children list."""
        
        self.children.remove(child)
        
    def remove_child_by_idx(self, idx):
        """Removes the child at idx in Node's children list."""
        
        del self.children[idx]

    def is_root(self):
        return self.root
            
    def make_copy(self):
        """Creates copy of this node.
        
        Does not copy parent and children pointers."""
        
        return Node(self.op, self.type, None, self.hp, self.comp_op,
                    self.turns_since_spawn, self.rloc_type, (self.rloc[0], self.rloc[1]),
                    self.direction, self.not_op, self.root)
                    
    def evaluate(self, game, robot, ally_fut, attack_fut):
        """Recursive evaluation of this Node and it's children given game state."""
        
        result = False
        dir_result = self.direction
        # First handle this node's expression
        if self.type == "SPAWN":
            if self.comp_op == "LT" and self.turns_since_spawn > (game['turn'] % 10):
                result = True
            elif self.comp_op == "GT" and self.turns_since_spawn < (game['turn'] % 10):
                result = True
        elif self.type == "HP":
            if self.comp_op == "LT" and robot.hp < self.hp:
                result = True
            elif self.comp_op == "GT" and robot.hp > self.hp:
                result = True
        elif self.type == "RLOC":
            true_loc = (robot.location[0] + self.rloc[0], robot.location[1] + self.rloc[1])
            bots = game.get('robots')
            check_hp = False
            hp_to_check = 0
            if self.rloc_type == "ENEMY":
                if true_loc in bots.keys():
                    bot = bots[true_loc]
                    if bot.player_id != robot.player_id:
                        check_hp = True
                        hp_to_check = bot.hp
            elif self.rloc_type == "SPAWN":
                if 'spawn' in rg.loc_types(true_loc):
                    result = True
            elif self.rloc_type == "INVALID":
                if any(x in rg.loc_types(true_loc) for x in ['obstacle', 'invalid']):
                    result = True
            elif self.rloc_type == "EMPTY":
                if not any(x in rg.loc_types(true_loc) for x in ['obstacle', 'invalid']):
                    if true_loc not in bots.keys():
                        result = True
            elif self.rloc_type == "ALLY":
                if true_loc in bots.keys():
                    bot = bots[true_loc]
                    if bot.player_id == robot.player_id:
                        check_hp = True
                        hp_to_check = bot.hp
            elif self.rloc_type == "ALLY_FUT":
                if not any(x in rg.loc_types(true_loc) for x in ['obstacle', 'invalid']):
                    hp_to_check = ally_fut[true_loc[0]][true_loc[1]]
                    if hp_to_check > 0:
                        check_hp = True
            elif self.rloc_type == "ATT_FUT":
                if not any(x in rg.loc_types(true_loc) for x in ['obstacle', 'invalid']):
                    result = (attack_fut[true_loc[0]][true_loc[1]] > 0)
            if check_hp:
                if self.comp_op == "LT" and hp_to_check < self.hp:
                    result = True
                elif self.comp_op == "GT" and hp_to_check > self.hp:
                    result = True
        if self.not_op:
            result = not result
            
        # Now check children Nodes
        # Precedence of True evalutations:
        #    True OR child > True AND children + True self > No AND children + True self
        #    Direction is set by the "lowest in the tree" True node of the highest
        #        precedence condition. For example, a True node with all True AND
        #        children and two True OR children will use the direction of the first True
        #        OR child. Assuming non-contradictory Node expressions, this should allow
        #        every Node to determine the direction in at least one game state.
        and_still_possible = True
        for child in self.children:
            ch_result = child.evaluate(game, robot, ally_fut, attack_fut)
            if result and (child.op == "AND"):
                and_still_possible = (and_still_possible and ch_result[0])
                dir_result = ch_result[1]
            if child.op == "OR" and ch_result[0]:
                return ch_result
        return ((result and and_still_possible), dir_result)
            
    def debug_print(self, indent=0):
        i_str = ""
        for x in range(indent):
            i_str = i_str + " "
        print i_str + "parent:", self.parent
        print i_str + "root:", self.root, "op:", self.op, "not:", self.not_op, \
                "type:", self.type, \
                "rloc:", self.rloc, "rloc_type:", self.rloc_type, "comp_op:", self.comp_op, \
                "hp:", self.hp, "spawn:", self.turns_since_spawn, "dir:", self.direction
        print i_str + "num children:", len(self.children)
        for child in self.children:
            print i_str + "child:", child
            child.debug_print(indent+1)
        
