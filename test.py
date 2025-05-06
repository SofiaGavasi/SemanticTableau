from tree import TreeNode
from text_processing import text_label, text_label_complete


import spacy
nlp = spacy.load("en_core_web_sm")

from rich.console import Console
from rich.table import Table
import re
import warnings





warnings.filterwarnings("ignore")


TreeNode.reset_tree()


#text = "if some cats and all dogs or some birds eat meat then they fly when they play"
#text = "Something happened. so, I got an umbrella, because it is raining"
#text = "birds and all dogs eat the meat or all grains and grass"
text = "male athletes can play"
text = "if Brian is heavy and Brian is fish then Brian is grey"
text = "Jane and Mary and Jake own a pet"

text = "All fruits that are unripe are not tasty. If a fruit is not tasty then Lucy is not satisfied. Some apples are unripe and all apples are fruit."
#Alice and Bob are knight or liar
#Alice tells truth if and only if Alice and Bob are liar
#Alice doesn’t lies if and only if Alice and Bob are liar
#All who are knight don’t lie
#All who are liars lie
text = "Nobody that does not have tail is playful."
text = "everyone who has a racket plays tennis"




# Some dreams are nights. Some nights are days.
#conclusion 1:  All days are either nights or dreams.

lemma_tags = {"NNS", "NNPS"}

doc = nlp(text)
for token in doc:
     print(f"Token: {token.text}, Type: {token.dep_}, Head: {token.head.text}")
     print(token, token.pos_)
    


    

statements_df = text_label_complete(text)

table = Table(title="My DataFrame") #display with rich
console = Console()
for column in statements_df.columns:
    table.add_column(column)
for index, row in statements_df.iterrows():
    table.add_row(*map(str, row))
console.print(table)

