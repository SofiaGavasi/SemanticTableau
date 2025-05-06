import re
import pandas as pd
import spacy
from text_processing import text_label
from solver import make_tree_inference
from collections import defaultdict
from itertools import product
import pandas as pd
import warnings
from itertools import combinations
from tree import TreeNode
warnings.filterwarnings("ignore")
statements = {
    "Subject": [],
    "Verb": [],
    "Object": []
}

pos_df = pd.DataFrame(statements)

premises = "Mary is human. Mary dies. Mary is happy. Brian is human. Brian is not happy."
conclusion = "Brian dies"
TreeNode.reset_tree()
root, boolean = make_tree_inference(premises, conclusion)

print("Are all contradictions?")
print (boolean)

sentences = [s.strip() for s in premises.split('.') if s.strip()]
print(sentences)



for sent in sentences:
    sentence_df = text_label(sent)
    or_sentence = sentence_df.loc[0, "Full sentence"]
    sentence_split = or_sentence.split()
    subject = sentence_split[int(sentence_df.loc[0, "Subject"])]
    verb = sentence_split[int(sentence_df.loc[0, "Verb"])]
    obj_index = sentence_df.loc[0, "Obj"]
    obj = None
    if obj_index:
        obj = sentence_split[int(obj_index)]
    statements["Subject"].append(subject)
    statements["Verb"].append(verb)
    statements["Object"].append(obj)
print(statements)


subject_indices = defaultdict(list)
for idx, subject in enumerate(statements['Subject']):
    subject_indices[subject].append(idx)

print(subject_indices)

new_sentences = []
for subject, indices in subject_indices.items():
    if len(indices) > 1:
        for i, j in product(indices, repeat=2):
            if i != j: 
                verb1, obj1 = statements['Verb'][i], statements['Object'][i]
                verb2, obj2 = statements['Verb'][j], statements['Object'][j]
                if obj1 is None and obj2 is None:
                    sentence = f"If one {verb1} then one {verb2}."
                elif obj1 is None:
                    sentence = f"If one {verb1} then one {verb2} {obj2}."
                elif obj2 is None:
                    sentence = f"If one {verb1} {obj1} then one {verb2}."
                else:
                    sentence = f"If one {verb1} {obj1} then one {verb2} {obj2}."
                new_sentences.append(sentence)


valid_statements = []
probable_statements = []
for s in new_sentences:
    test_premises = premises + " " + s
    TreeNode.reset_tree()
    root, boolean = make_tree_inference(test_premises, "")
    if not boolean: 
        valid_statements.append(s)
        TreeNode.reset_tree()
        root, boolean = make_tree_inference(test_premises, conclusion)
        if boolean:
            probable_statements.append(s)


if probable_statements:
    print("The rules that seem possible given the initial premises and conclusion are:")
    for s in probable_statements:
        print("-", s)





# max_non_contradictory_set = []

# for r in range(2, len(valid_statements) + 1):  
#     for combo in combinations(valid_statements, r):
#         test_premises = premises + " " + ' '.join(combo)
#         TreeNode.reset_tree()
#         root, boolean = make_tree_inference(test_premises, "")
#         if not boolean:
#             if len(combo) > len(max_non_contradictory_set):
#                 max_non_contradictory_set = list(combo)


# print("Largest set of inferred statements that do NOT contradict:")
# for stmt in max_non_contradictory_set:
#     print("-", stmt)

# final_premises = premises + " " + ' '.join(max_non_contradictory_set)
# TreeNode.reset_tree()
# root, boolean = make_tree_inference(final_premises, conclusion)
# print("Are all contradictions?")
# print (boolean)