from tree import TreeNode
from text_processing import text_label

from solver import make_tree
from solver import make_tree_inference

import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")
from IPython.display import display
from tabulate import tabulate
from rich.console import Console
from rich.table import Table
from nicegui import ui
import warnings


warnings.filterwarnings("ignore")



def main():
   
    TreeNode.reset_tree()


    #text = "if some cats and all dogs or some birds eat meat then they fly when they play"
    #text = "Something happened. so, I got an umbrella, because it is raining"
    #text = "birds and all dogs eat the meat or all grains and grass"
    text = "If nobody sings, then a teacher eats a book. Nobody sings."
    conclusion = "A teacher eats a book."


  



    #doc = nlp(text)
    #for token in doc:
         #print(f"Token: {token.text}, Type: {token.dep_}, Head: {token.head.text}")

    statements_df = text_label(text + " "+ conclusion)
 
    #conclusions_df = text_label(conclusion)
      
    

    table = Table(title="My DataFrame") #display with rich
    console = Console()
    for column in statements_df.columns:
        table.add_column(column)
    for index, row in statements_df.iterrows():
        table.add_row(*map(str, row))
    console.print(table)


    #root, boolean = make_tree(text, 1) 
    root, boolean = make_tree_inference(text, conclusion)

    print("Are all contradictions?")
    print (boolean)

    #root.display_tree(0)

    tree_data = root.to_nicegui_format()


    tree = ui.tree([tree_data], label_key='id', on_select=lambda e: ui.notify(f"Node selected: {e.value}"))

    tree.add_slot('default-header', '''
        <span :props="props" :style="{ color: props.node.color }">
            Node <strong>{{ props.node.id }}</strong>
        </span>
    ''')

    tree.add_slot('default-body', '''
        <span :props="props">
            <div v-html="props.node.description"></div>  <!-- Render the DataFrame HTML -->
        </span>
    ''')

    ui.run()

    
   
    

if __name__ in {"__main__", "__mp_main__"}:
    main()