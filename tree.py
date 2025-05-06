import pandas as pd
from rich.console import Console
from rich.table import Table

pd.set_option('display.max_colwidth', None)

class TreeNode:
    node_counter = 0 
    console = Console()  

    def __init__(self, value=None):
        self.value = value    
        self.children = []           
        self.node_id = TreeNode.node_counter 
        TreeNode.node_counter += 1        

    def add_child(self, child_node):
        self.children.append(child_node)

    def display_tree(self, level=0, parent_id=None):
        parent_info = f"(Parent ID: {parent_id})" if parent_id is not None else "(Root)"
        description = f"ID: {self.node_id}, {parent_info}"
        TreeNode.console.print(description)

        if isinstance(self.value, pd.DataFrame):
            self.display_dataframe(self.value)

        for child in self.children:
            child.display_tree(level + 1, self.node_id) 

    def display_node(self):
        if isinstance(self.value, pd.DataFrame):
            self.display_dataframe(self.value)

    def display_dataframe(self, df):
        """Display a pandas DataFrame using rich tables."""
        table = Table(title="Node DataFrame")
      
        for column in df.columns:
            table.add_column(column, justify="center")

        for _, row in df.iterrows():
            table.add_row(*[str(cell) for cell in row])

        TreeNode.console.print(table)

    def get_last_child(self):
        if self.children:
            return self.children[-1]
        return None 
    # def to_nicegui_format(self):
    #     node_data = {
    #         'id': str(self.node_id),  
    #         'description': self.get_dataframe_html(),  
    #         'children': [child.to_nicegui_format() for child in self.children]  
    #     }
    #     return node_data
    def to_nicegui_format(self, branch_color=None):
        color = branch_color or f"hsl({(self.node_id * 37) % 360}, 70%, 50%)"
        node_data = {
            'id': str(self.node_id),
            'description': self.get_dataframe_html(),
            'color': color,
            'children': [
                child.to_nicegui_format(branch_color=color if len(self.children) == 1 else None)
                for child in self.children
            ],
        }
        return node_data
    def get_dataframe_html(self):
       
        if isinstance(self.value, pd.DataFrame):
            html_table = self.value.to_html(classes="dataframe", index=False)

            styled_html = f"""
            <style>
                .dataframe {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                .dataframe th, .dataframe td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                .dataframe th {{
                    background-color: #f2f2f2;
                    font-weight: bold;
                }}
                .dataframe td {{
                    background-color: #fafafa;
                }}
            </style>
            {html_table}
            """
            return styled_html
        return "No data available" 

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
