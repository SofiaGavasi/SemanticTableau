import pandas as pd


pd.set_option('display.max_colwidth', None)

class TreeNode:
    node_counter = 0 

    def __init__(self, value=None):
        self.value = value    
        self.children = []           
        self.node_id = TreeNode.node_counter 
        TreeNode.node_counter += 1        

    def add_child(self, child_node):
        self.children.append(child_node)


    def display_node(self):
        if isinstance(self.value, pd.DataFrame):
            self.display_dataframe(self.value)


    def get_last_child(self):
        if self.children:
            return self.children[-1]
        return None 
 

    def clean_dataframe(self):
        
        if isinstance(self.value, pd.DataFrame):
            for column in self.value.columns:
                # If the column values are lists (e.g., ["", "a", "b"]), we clean them
                if self.value[column].apply(lambda x: isinstance(x, list)).any():
                    self.value[column] = self.value[column].apply(lambda x: [item for item in x if item != ""])
                # If the column values are strings (e.g., ""), we clean them
                elif self.value[column].apply(lambda x: isinstance(x, str)).any():
                    self.value[column] = self.value[column].apply(lambda x: "" if x == "" else x)
        return self.value
    
    @classmethod
    def reset_tree(cls):
        cls.node_counter = 0
