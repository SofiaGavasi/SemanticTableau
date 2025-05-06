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

    conclusion = "Jane has bird."
    text = "Jane and Bill and Kelly own fish or dog or bird. someone owns bird if and only if someone owns not dog and fish. anyone owns dog if and only if anyone owns not bird and fish. anyone owns fish if and only if anyone owns not dog and bird."

    text = "Karen plays badminton or tennis or football. If Karen plays tennis, then Karen does not play football and badminton. If Karen plays badminton, then she does not play tennis and football. If Karen plays football, then Karen does not play tennis and badminton. Karen is a kicker. All kickers play football."
    conclusion = "Karen plays football"

    text = "Karen plays badminton or tennis or football. If Karen plays tennis, then Karen does not play football and badminton. If Karen plays badminton, then she does not play tennis and football. If Karen plays football, then Karen does not play tennis and badminton. Karen is a kicker. All kickers play football. John plays badminton or tennis or football. If John plays tennis, then John does not play football and badminton. If John plays football, then John does not play tennis and badminton. If John plays badminton, then John does not play tennis and football. John is a racketier. All racketiers play tennis."   
    conclusion = "John plays tennis"

    text = "Jenny plays dance or tennis or football. If Jenny plays tennis, then Jenny does not play football and dance. If Jenny plays football, then Jenny does not play tennis and dance. If Jenny plays dance, then Jenny does not play tennis and football. Karen plays football. John plays tennis. If one plays football, then Jenny does not play football. If one plays tennis, then Jenny does not play tennis."
    conclusion = "Jenny plays dance"
   
    text = "Alice and Bob are knight or liar. Alice is liar if and only if Alice or Bob are knight. Alice is knight if and only if Alice and Bob are liar. All who are liar are not knight. All who are knight are not liar."
    conclusion ="Alice is liar"

 

    text = "All film stars are singers. All film directors are film stars." 
    conclusion = "Some film stars are film directors."
    conclusion = "All film directors are singers."

    text = "If some fruit is not tasty then Lucy is not satisfied. Some apples are unripe and all apples are fruit. All fruit that are unripe are not tasty."
    conclusion = "Lucy is not satisfied"

    text = "No ducks waltz. No officers don't waltz. all poultry are ducks"
    conclusion = "some ducks are officers"

    text = "Nobody that loves fish is not teachable. Nobody that does not have tail is playful. All who have whiskers love fish. Nobody that is teachable has green-eyes. All who do not have whiskers do not have tail."
    conclusion = "All that have green-eyes are not playful."


    
    text = "Karen and John and Jenny play soccer or tennis or football. If one plays tennis then one does not play football and soccer. If one plays football then one does not play tennis and soccer. If one plays soccer then one does not play tennis and football. All who kick balls play football. All who have a racket play tennis. Karen kicks balls. John has a racket. If someone plays football then Jenny does not play football. If someone plays tennis then Jenny does not play tennis. If someone plays soccer then Jenny does not play soccer."
 
    conclusion = "Jenny plays football"

    text = "Nobody that is experienced is not competent. Jenkins is blundering. Nobody that is competent is blundering."
    conclusion = "Jenkins is not experienced"






    #doc = nlp(text)
    #for token in doc:
         #print(f"Token: {token.text}, Type: {token.dep_}, Head: {token.head.text}")

    statements_df = text_label(text)
 
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