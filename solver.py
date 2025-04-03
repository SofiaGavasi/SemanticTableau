from tree import TreeNode
import pandas as pd
import spacy
nlp = spacy.load("en_core_web_sm")
from text_processing import text_label
from negating import negate_level_5
from contradictions import find_contradictions
import re


lemma_tags = {"NNS", "NNPS"}


data1 = {
        "key": [],
        "value": []
    }


data2 = {
    "key": [
        "Alice", "Brian", "Catherine", "David", "Emma", "Frank", "Grace",
        "Hannah", "Isaac", "Jack", "Katherine", "Liam", "Mia", "Nathan",
        "Olivia", "Paul", "Quinn", "Rachel", "Sophia", "Thomas", "Uma",
        "Victor", "William", "Xander", "Yasmine", "Zachary"
    ],
    "value": [""] * 26 
}


constants_df = pd.DataFrame(data1)

variables_df = pd.DataFrame(data2)



def solve_level_1(sentence, root, sign):

    sentence_df = text_label(sentence)
    node_1_true = []
    node_2_true = []
    node_1_false = []
    node_2_false = []
    children = []
    highlighted = []
    for i in sentence_df['Direct parent'].index: 
        if sentence_df.at[i, 'Direct parent'] == 0:
            children.append(i)
    
    if sign <0:
        rule = 8
        node_1_true.append(sentence_df.loc[children[0], 'Full sentence']) 
        node_1_false.append(sentence_df.loc[children[1], 'Full sentence'])
        node_2_true.append(sentence_df.loc[children[1], 'Full sentence']) 
        node_2_false.append(sentence_df.loc[children[0], 'Full sentence'])  
        highlighted = node_1_true+node_1_false+node_2_true+node_2_false


    else:
        rule = 7
        node_1_true.append(sentence_df.loc[children[0], 'Full sentence']) 
        node_1_true.append(sentence_df.loc[children[1], 'Full sentence'])
        node_2_false.append(sentence_df.loc[children[0], 'Full sentence']) 
        node_2_false.append(sentence_df.loc[children[1], 'Full sentence']) 
        highlighted = node_1_true+node_1_false+node_2_true+node_2_false
    df_node_1 = pd.DataFrame({
        'True Statements': [node_1_true],
        'False Statements': [node_1_false],
        'End': [False],
        'Contradiction': [False],
            'Rule': [rule],
                'Highlight': [highlighted],
                'Parent': [sentence]
    })    
    df_node_2 = pd.DataFrame({
        'True Statements': [node_2_true],
        'False Statements': [node_2_false],
        'End': [False],
        'Contradiction': [False],
            'Rule': [rule],
                'Highlight': [highlighted],
                'Parent': [sentence]
    })  
    
    child_node = TreeNode(df_node_1)
    root.add_child(child_node)
    child_node = TreeNode(df_node_2)
    root.add_child(child_node)  



def solve_level_0(statements_df, index, current_parent, sign):
    parent_sentence = statements_df.loc[0, "Full sentence"]
    if sign <0:
        iterations = 1
        statements = []
        for i in statements_df['Direct parent'].index: #  separating each child in diff branches (since they are separated by period, therefore and statement, and negated)
            if statements_df.at[i, 'Direct parent'] == index:

                # current_child = i
                # if iterations ==1:
                #     df_child = pd.DataFrame({
                #         'True Statements': [""],
                #         'False Statements': [statements_df.loc[current_child, "Full sentence"]],
                #         'End': [False],
                #         'Contradiction': [False]
                #     })
                #     child_node = TreeNode(df_child)
                #     current_parent.add_child(child_node)
                # else:
                #     statements+=statements_df.loc[current_child, "Full sentence"]
                #     statements += ". "
                # iterations +=1
                current_child = i
                statements.append(statements_df.loc[current_child, "Full sentence"])
        df_child = pd.DataFrame({
            'True Statements': [""],
            'False Statements': [statements],
            'End': [False],
            'Contradiction': [False],
            'Rule': [0],
            'Highlight': [""],       
            'Parent': [""]
            
        })
        child_node = TreeNode(df_child)
        current_parent.add_child(child_node)
    else:
        statements = []
        for i in statements_df['Direct parent'].index: #  separating each child in same branch (since they are separated by period, therefore and statement)
            if statements_df.at[i, 'Direct parent'] == index:
                current_child = i
                statements.append(statements_df.loc[current_child, "Full sentence"])

        df_child = pd.DataFrame({
            'True Statements': [statements],
            'False Statements': [""],
            'End': [False],
            'Contradiction': [False],
            'Rule': [0],
            'Highlight': [""],       
            'Parent': [""]
        })
        child_node = TreeNode(df_child)
        current_parent.add_child(child_node)



def solve_level_2(statements_df, index, root, sign):
    children = []
    parent_sentence = statements_df.loc[0, "Full sentence"]
    for i in statements_df['Direct parent'].index:
        if statements_df.at[i, 'Direct parent'] == index:
            children.append(i)
    
    ifthen_op = str(statements_df.loc[index, "If-then operator"])
    and_op = str(statements_df.loc[index, "And operator"])
    or_op = str(statements_df.loc[index, "Or operator"])
    updated = False

    if len(children)>2:
        #case: 01 and, 01 if-then (if Brian is heavy and Brian is a fish then Brian is happy)
        if "01" in ifthen_op and "01" in and_op:
            updated = True
            if sign <0:
                highlighted = []
                highlighted.append(statements_df.loc[children[0], "Full sentence"] + " and " + statements_df.loc[children[1], "Full sentence"])
                highlighted.append(statements_df.loc[children[2], "Full sentence"])
                df_node = pd.DataFrame({
                    'True Statements': [statements_df.loc[children[0], "Full sentence"] + " and " + statements_df.loc[children[1], "Full sentence"] ],
                    'False Statements': [statements_df.loc[children[2], "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [6],
                    'Highlight': [true_statements],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
            else:
                highlighted1 = []
                highlighted2 = []
                highlighted1.append(statements_df.loc[children[0], "Full sentence"] + " and " + statements_df.loc[children[1], "Full sentence"])
                highlighted2.append(statements_df.loc[children[2], "Full sentence"])
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [statements_df.loc[children[0], "Full sentence"] + " and " + statements_df.loc[children[1], "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted1],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                df_node = pd.DataFrame({
                    'True Statements': [statements_df.loc[children[2], "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted2],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 

        #case: 12 and, 01 if-then (if Brian is heavy then Brian is a fish and Brian is happy)
        elif "01" in ifthen_op and "12" in and_op:
            updated = True
            if sign <0:
                highlighted = []
                highlighted.append(statements_df.loc[children[1], "Full sentence"] + " and " + statements_df.loc[children[2], "Full sentence"])
                highlighted.append(statements_df.loc[children[0], "Full sentence"])
                df_node = pd.DataFrame({
                    'True Statements': [statements_df.loc[children[0], "Full sentence"] ],
                    'False Statements': [ statements_df.loc[children[1], "Full sentence"] +" and "+statements_df.loc[children[2], "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [6],
                    'Highlight': [true_statements],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
            else:
                highlighted1 = []
                highlighted2 = []
                highlighted1.append(statements_df.loc[children[1], "Full sentence"] + " and " + statements_df.loc[children[2], "Full sentence"])
                highlighted2.append(statements_df.loc[children[0], "Full sentence"])
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [statements_df.loc[children[0], "Full sentence"] ],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted2],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                df_node = pd.DataFrame({
                    'True Statements': [ statements_df.loc[children[1], "Full sentence"] +" and "+statements_df.loc[children[2], "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted1],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 


    if updated == False:

        children_without_0 = ""
        for i, child in enumerate(children):
            if i>0:
                string = str(i)+str(i+1)

                if string in ifthen_op: # I am happy and if I cry then I am sad
                    children_without_0+= "if "
                    children_without_0 += statements_df.loc[child, "Full sentence"]
                    children_without_0+= " then "
                else:
                    children_without_0 += statements_df.loc[child, "Full sentence"]
                    weird_string = str(i+1)+ str(i)
                    if string in and_op:
                        children_without_0+= " and "
                    elif string in or_op:
                        children_without_0+= " or "
                    elif weird_string in ifthen_op: #I am happy and I cry when I am sad
                        children_without_0+= " when "


        if "01" in ifthen_op:
            if sign <0:
                highlighted = []
                highlighted.append(statements_df.loc[children[0], "Full sentence"])
                highlighted.append(children_without_0)
                df_node = pd.DataFrame({
                    'True Statements': [statements_df.loc[children[0], "Full sentence"]],
                    'False Statements': [children_without_0],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [6],
                    'Highlight': [highlighted],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
            else:
                highlighted_parts1 = []
                highlighted_parts2 = []
                highlighted_parts1.append(statements_df.loc[children[0], "Full sentence"])
                highlighted_parts2.append(children_without_0)
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [statements_df.loc[children[0], "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted_parts1],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                df_node = pd.DataFrame({
                    'True Statements': [children_without_0],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted_parts2],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
        elif "10" in ifthen_op:
            highlighted = []
            highlighted.append(statements_df.loc[children[0], "Full sentence"])
            highlighted.append(children_without_0)
            if sign <0:
                df_node = pd.DataFrame({
                    'True Statements': [children_without_0],
                    'False Statements': [statements_df.loc[children[0], "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [6],
                    'Highlight': [highlighted],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
            else:
                highlighted_parts1 = []
                highlighted_parts2 = []
                highlighted_parts1.append(statements_df.loc[children[0], "Full sentence"])
                highlighted_parts2.append(children_without_0)
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [children_without_0],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted_parts2],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                df_node = pd.DataFrame({
                    'True Statements': [statements_df.loc[children[0], "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [5],
                    'Highlight': [highlighted_parts1],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 

        elif "01" in and_op:
            highlighted_parts1 = []
            highlighted_parts2 = []
            highlighted_parts1.append(statements_df.loc[children[0], "Full sentence"])
            highlighted_parts2.append(children_without_0)
            if sign <0:
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [statements_df.loc[children[0], "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [2],
                    'Highlight': [highlighted_parts1],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [children_without_0],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [2],
                    'Highlight': [highlighted_parts2],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
            else:
                true_statements = []
                true_statements.append(statements_df.loc[children[0], "Full sentence"])
                true_statements.append(children_without_0)
                df_node = pd.DataFrame({
                    'True Statements': [true_statements],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [1],
                    'Highlight': [true_statements],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 

        elif "01" in or_op:

            if sign <0:
                false_statements = []
                false_statements.append(statements_df.loc[children[0], "Full sentence"])
                false_statements.append(children_without_0)
                df_node = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [false_statements],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [4],
                    'Highlight': [false_statements],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 

            else:
                highlighted_parts1 = []
                highlighted_parts2 = []
                highlighted_parts1.append(statements_df.loc[children[0], "Full sentence"])
                highlighted_parts2.append(children_without_0)
                df_node = pd.DataFrame({
                    'True Statements': [statements_df.loc[children[0], "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [3],
                    'Highlight': [highlighted_parts1],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                df_node = pd.DataFrame({
                    'True Statements': [children_without_0],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [3],
                    'Highlight': [highlighted_parts2],
                    'Parent': [parent_sentence]
                })  
                child_node = TreeNode(df_node)
                root.add_child(child_node) 
                


def solve_level_3(statements_df, index, root, sign):
    children = []
    parent_sentence = statements_df.loc[0, "Full sentence"]
    
    for i in statements_df['Direct parent'].index:
        if statements_df.at[i, 'Direct parent'] == index:
            children.append(i)
    
    and_op = str(statements_df.loc[index, "And operator"])
    or_op = str(statements_df.loc[index, "Or operator"])

    children_without_0 = ""
    for i, child in enumerate(children):
        if i>0:
            children_without_0 += statements_df.loc[child, "Full sentence"]
            string = str(i)+str(i+1)
            if string in and_op:
                children_without_0+= " and "
            elif string in or_op:
                children_without_0+= " or "
            

    if "01" in and_op:
        if sign <0:
            highlighted_parts1 = []
            highlighted_parts2 = []
            highlighted_parts1.append(statements_df.loc[children[0], "Full sentence"])
            highlighted_parts2.append(children_without_0)
            df_node = pd.DataFrame({
                'True Statements': [""],
                'False Statements': [statements_df.loc[children[0], "Full sentence"]],
                'End': [False],
                'Contradiction': [False],
                    'Rule': [2],
                'Highlight': [highlighted_parts1],
                'Parent': [parent_sentence]
            })  
            child_node = TreeNode(df_node)
            root.add_child(child_node) 
            df_node = pd.DataFrame({
                'True Statements': [""],
                'False Statements': [children_without_0],
                'End': [False],
                'Contradiction': [False],
                    'Rule': [2],
                'Highlight': [highlighted_parts2],
                'Parent': [parent_sentence]
            })  
            child_node = TreeNode(df_node)
            root.add_child(child_node) 
        else:
            true_statements = []
            true_statements.append(statements_df.loc[children[0], "Full sentence"])
            true_statements.append(children_without_0)
            df_node = pd.DataFrame({
                'True Statements': [true_statements],
                'False Statements': [""],
                'End': [False],
                'Contradiction': [False],
                    'Rule': [1],
                'Highlight': [true_statements],
                'Parent': [parent_sentence]
            })  
            child_node = TreeNode(df_node)
            root.add_child(child_node) 

    elif "01" in or_op:

        if sign <0:
            false_statements = []
            false_statements.append(statements_df.loc[children[0], "Full sentence"])
            false_statements.append(children_without_0)
            df_node = pd.DataFrame({
                'True Statements': [""],
                'False Statements': [false_statements],
                'End': [False],
                'Contradiction': [False],
                    'Rule': [4],
                'Highlight': [false_statements],
                'Parent': [parent_sentence]
            })  
            child_node = TreeNode(df_node)
            root.add_child(child_node) 

        else:
            highlighted_parts1 = []
            highlighted_parts2 = []
            highlighted_parts1.append(statements_df.loc[children[0], "Full sentence"])
            highlighted_parts2.append(children_without_0)
            df_node = pd.DataFrame({
                'True Statements': [statements_df.loc[children[0], "Full sentence"]],
                'False Statements': [""],
                'End': [False],
                'Contradiction': [False],
                    'Rule': [3],
                'Highlight': [highlighted_parts1],
                'Parent': [parent_sentence]
            })  
            child_node = TreeNode(df_node)
            root.add_child(child_node) 
            df_node = pd.DataFrame({
                'True Statements': [children_without_0],
                'False Statements': [""],
                'End': [False],
                'Contradiction': [False],
                    'Rule': [3],
                'Highlight': [highlighted_parts2],
                'Parent': [parent_sentence]
            })  
            child_node = TreeNode(df_node)
            root.add_child(child_node) 
  

def get_leaves(node):
    if not node.children:
        return [node]
    
    leaves = []
    for child in node.children:
        leaves.extend(get_leaves(child))
    return leaves

def get_item(sentence_df, what):
    or_sentence = sentence_df.loc[0, "Full sentence"]
    sentence_split = or_sentence.split()

    sub_index = sentence_df.loc[0, what]
    subject = []

    if sub_index == "":
        #print(what +  " MISSING, SOLVER")
        return ""
        #raise ValueError("SUBJECT/OBJECT/VERB MISSING, SOLVER")
    else:
        int_list = [int(c) for c in sentence_df.loc[0, what]]
        for i,item in enumerate(int_list):
            subject.append(sentence_split[item])
        return " ".join(subject).strip()

def lemmatize(words):
    if words != "":
        word_lemma = []
        doc = nlp(words)
        for token in doc:
            if token.tag_ in lemma_tags:   
                word_lemma.append(token.lemma_)
            else:
                word_lemma.append(token.text)
        return " ".join(word_lemma).strip()
    else: return ""



def create_variable(sentence_df, sign, existential, quantifier, negate):
    or_sentence = sentence_df.loc[0, "Full sentence"]
    sentence_split = or_sentence.split()
    global variables_df
    
    if existential:
        existentials = sentence_df.loc[0, quantifier].split()
        for i,word in enumerate(existentials[:-1]):  
            first_empty_key = variables_df.loc[variables_df['value'] == '', 'key'].iloc[0]

            subject = lemmatize(get_item(sentence_df, "Subject"))
            obj = lemmatize(get_item(sentence_df, "Obj"))
            verb = get_item(sentence_df, "Verb")
            adjective = False
            if len(subject.split())>1:
                adjective = True
                subjects = subject.split()
            verb_lemma = ""
            doc = nlp(verb)
            for token in doc:
                verb_lemma = token.lemma_
            if verb_lemma == "be" and obj == "":
                if len(sentence_split) > int(sentence_df.loc[0, "Verb"])+1:
                    obj = sentence_split[int(sentence_df.loc[0, "Verb"])+1]
                    doc = nlp(or_sentence)
                    for k,tok in enumerate(doc):
                        if k ==int(sentence_df.loc[0, "Verb"])+1 and (tok.dep_ == "det" or tok.pos_ == "DET") :        
                            obj = sentence_split[int(sentence_df.loc[0, "Verb"])+2]
                
            
            values = []
            new_sentences = ""
            values.append(subject)
            if existentials[i+1] == "subj": # some cats are....
                if int(existentials[i]) == int(sentence_df.loc[0, "Subject"]): # someone is happy
                    if verb_lemma == "be":
                        new_sentences = first_empty_key + " is " + obj
                    elif obj != "":
                        new_sentences =first_empty_key + " "+ verb+ " "+ obj
                    else:
                        new_sentences = first_empty_key + " "+ verb
                else:
                    if adjective:
                        if verb_lemma == "be":
                            new_sentences = first_empty_key + " is " + subjects[0]+" and "+first_empty_key + " is " + subjects[1] + " and " + first_empty_key + " is " + obj
                        elif obj != "":
                            new_sentences = first_empty_key + " is " + subjects[0]+" and "+first_empty_key + " is " + subjects[1] +  + " and " + first_empty_key + " "+ verb+ " "+ obj
                        else:
                            new_sentences = first_empty_key + " is " + subjects[0]+" and "+first_empty_key + " is " + subjects[1] +  + " and " + first_empty_key + " "+ verb

                    else:
                        if verb_lemma == "be":
                            new_sentences = first_empty_key + " is " + subject + " and " + first_empty_key + " is " + obj
                        elif obj != "":
                            new_sentences = first_empty_key + " is " + subject + " and " + first_empty_key + " "+ verb+ " "+ obj
                        else:
                            new_sentences = first_empty_key + " is " + subject + " and " + first_empty_key + " "+ verb
                        
            
            elif existentials[i+1] == "obj": 
                if int(existentials[i]) == int(sentence_df.loc[0, "Obj"]): # Mary hates someone
                    
                    new_sentences =subject + " "+ verb+ " "+ first_empty_key
                    values.append(subject + " "+ verb)
                    
                else: # Mary hates some cats
                    new_sentences = first_empty_key + " is " + obj + " and " + subject + " "+ verb+ " "+ first_empty_key
                    values.append(subject)
                    values.append( obj)

            row_index = variables_df.loc[variables_df['key'] == first_empty_key].index[0]
            variables_df.at[row_index, 'value'] = values
            
            return new_sentences

    else:
        existentials = sentence_df.loc[0, quantifier].split() # calling it the same out of laziness, this is universal

        for i,word in enumerate(existentials[:-1]):  
          
            first_empty_key = variables_df.loc[variables_df['value'] == '', 'key'].iloc[0]
            
            subject = lemmatize(get_item(sentence_df, "Subject"))
            obj = lemmatize(get_item(sentence_df, "Obj"))
            verb = get_item(sentence_df, "Verb")
            adjective = False
            if len(subject.split())>1:
                adjective = True
                subjects = subject.split()
            verb_lemma = ""
            doc = nlp(verb)
            for token in doc:
                verb_lemma = token.lemma_
            if verb_lemma == "be" and obj == "":
                if len(sentence_split) > int(sentence_df.loc[0, "Verb"])+1:
                    obj = sentence_split[int(sentence_df.loc[0, "Verb"])+1]
                    doc = nlp(or_sentence)
                    for k,tok in enumerate(doc):
                        if k ==int(sentence_df.loc[0, "Verb"])+1 and (tok.dep_ == "det" or tok.pos_ == "DET") :        
                            obj = sentence_split[int(sentence_df.loc[0, "Verb"])+2]

            values = []
            new_sentences = ""
            values.append(subject)
            if existentials[i+1] == "subj": # some cats are....

                if int(existentials[i]) == int(sentence_df.loc[0, "Subject"]): # everyone is happy
                    if verb_lemma == "be":
                        new_sentences = first_empty_key + " is " + obj
                    elif obj != "":
                        new_sentences =first_empty_key + " "+ verb+ " "+ obj
                    else:
                        new_sentences = first_empty_key + " "+ verb

                else:
                    if adjective:
                        if verb_lemma == "be":
                            new_sentences = "if " +first_empty_key + " is " + subjects[0] + " and " +first_empty_key + " is " + subjects[1] +" then " + first_empty_key + " is " + obj
                        elif obj != "":
                            new_sentences = "if " +first_empty_key + " is " +  subjects[0] + " and " +first_empty_key + " is " + subjects[1] + " then " + first_empty_key + " "+ verb+ " "+ obj
                        else:
                            new_sentences = "if " +first_empty_key + " is " +  subjects[0] + " and " +first_empty_key + " is " + subjects[1] + " then " + first_empty_key + " "+ verb

                    else:

                        if verb_lemma == "be":
                            new_sentences = "if " +first_empty_key + " is " + subject + " then " + first_empty_key + " is " + obj
                        elif obj != "":
                            new_sentences = "if " +first_empty_key + " is " + subject + " then " + first_empty_key + " "+ verb+ " "+ obj
                        else:
                            new_sentences = "if " +first_empty_key + " is " + subject + " then " + first_empty_key + " "+ verb
            
            elif existentials[i+1] == "obj": 
                if int(existentials[i]) == int(sentence_df.loc[0, "Subject"]): # Mary hates everyone
                    
                    new_sentences =subject + " "+ verb+ " "+ first_empty_key
                    values.append(subject + " "+ verb)
                else: #Mary hates every cat

                    new_sentences = "if " +first_empty_key + " is " + obj + " then " + subject + " "+ verb+ " "+ first_empty_key
                    values.append(subject)
                    values.append(verb + " "+ obj)
                



            row_index = variables_df.loc[variables_df['key'] == first_empty_key].index[0]
            variables_df.at[row_index, 'value'] = values
            
            return new_sentences
           
    #else: #TODO



def solve_sentence(sentence, root, sign):
    parent_sentence = sentence
    highlighted_parts = []
    sentence_df = text_label(sentence)
    index = 0

    if sentence_df.loc[index, "Height"] == 0: #sentences separated by periods
        solve_level_0(sentence_df, index, root, sign) 
                    
    elif sentence_df.loc[index, "Height"] == 1:
             
        solve_level_1(sentence_df.loc[index, "Full sentence"],root, sign)   
  

    elif sentence_df.loc[index, "Height"] == 2:
        
        if str(sentence_df.loc[index, "Not operator"]) != "":
            highlighted_parts.append(sentence_df.loc[index, "Full sentence"])
            if sign < 0:
                 df_child = pd.DataFrame({
                    'True Statements': [sentence_df.loc[index, "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [14],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                })
            else:
                df_child = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [sentence_df.loc[index, "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [13],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                })
            child_node = TreeNode(df_child)
            root.add_child(child_node)
        
        else:
            solve_level_2(sentence_df, index, root, sign)
    
    elif sentence_df.loc[index, "Height"] == 3:
         
        if str(sentence_df.loc[index, "Not operator"]) != "":
            highlighted_parts.append(sentence_df.loc[index, "Full sentence"])
            if sign < 0:
                 df_child = pd.DataFrame({
                    'True Statements': [sentence_df.loc[index, "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [14],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                })
            else:
                df_child = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [sentence_df.loc[index, "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [13],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                })
            child_node = TreeNode(df_child)
            root.add_child(child_node)
            
        else:
            solve_level_3(sentence_df, index, root, sign)
            
    elif sentence_df.loc[index, "Height"] == 4:
        if str(sentence_df.loc[index, "Not operator"]) != "":
            highlighted_parts.append(sentence_df.loc[index, "Full sentence"])
            if sign < 0:
                 df_child = pd.DataFrame({
                    'True Statements': [sentence_df.loc[index, "Full sentence"]],
                    'False Statements': [""],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [14],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                })
            else:
                df_child = pd.DataFrame({
                    'True Statements': [""],
                    'False Statements': [sentence_df.loc[index, "Full sentence"]],
                    'End': [False],
                    'Contradiction': [False],
                    'Rule': [13],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                })
            child_node = TreeNode(df_child)
            root.add_child(child_node)
        else:
            solve_level_3(sentence_df, index, root, sign) #works the same way

    elif sentence_df.loc[index, "Height"] == 5: #we should make it end here
        
        if  sentence_df.loc[0, "Not operator"] != "":
        
            result = negate_level_5(0, sentence_df)
            highlighted_parts.append(result)
            if sign >0:

                df_child = pd.DataFrame({
                        'True Statements': [""],         #TODO check if this is correct
                        'False Statements': [result],
                        'End': [False],
                        'Contradiction': [False],
                        'Rule': [13],
                        'Highlight': [highlighted_parts],
                        'Parent': [parent_sentence]
                    })
            else:
                df_child = pd.DataFrame({
                        'True Statements': [result],
                        'False Statements': [""],
                        'End': [False],
                        'Contradiction': [False],
                        'Rule': [14],
                        'Highlight': [highlighted_parts],
                        'Parent': [parent_sentence]
                    })
        
        elif sentence_df.loc[0, "Existential quantifier"] != "":
            if sign > 0:
                sentence = create_variable(sentence_df, sign, True, "Existential quantifier", False)
                highlighted_parts.append(sentence)
                df_child = pd.DataFrame({           #TODO check if this is correct
                            'True Statements': [sentence],
                            'False Statements': [""],
                            'End': [False],
                            'Contradiction': [False],
                            'Rule': [11],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                        })
                
        
        elif sentence_df.loc[0, "Universal quantifier"] != "":

            if sign < 0:
                sentence = create_variable(sentence_df, sign, False, "Universal quantifier", False)
                highlighted_parts.append(sentence)
                df_child = pd.DataFrame({           #TODO check if this is correct
                            'True Statements': [""],
                            'False Statements': [sentence],
                            'End': [False],
                            'Contradiction': [False],
                            'Rule': [10],
                            'Highlight': [highlighted_parts],
                            'Parent': [parent_sentence]
                        })

              
             
        child_node = TreeNode(df_child)
        root.add_child(child_node)


def transform_universal(sentence_df):
    # I get: All pens are pencils
    # Transform it to: It is not the case that Alice is a pen and Alice isn't a pencil

    #sentence = "it is not the case that " + create_variable(sentence_df, 1, True, "Universal quantifier", True)
    sentence = create_variable(sentence_df, -1, False, "Universal quantifier", False)
    return sentence

def transform_existential(sentence_df):
    # I get: some pens are pencils
    # Transform it to: It is not the case that if Alice is a pen then Alice is not a pencil
    
    #sentence = "it is not the case that " + create_variable(sentence_df, 1, False, "Existential quantifier", True)
    sentence = create_variable(sentence_df, 1, True, "Existential quantifier", False)
    return sentence


def add_all_variables(sentence_df, existential):
    # I get sentence: "all cats are animals"
    #  need to make it "if Alice is a cat then Alice is an Animal"

    keys = variables_df.loc[variables_df['value'] != '', 'key'].tolist()
    for other in constants_df.loc[constants_df['key'] != '', 'key'].tolist():
        keys.append(other)
    or_sentence = sentence_df.loc[0, "Full sentence"]
    sentence_split = or_sentence.split()

    if len(keys) < 1:
        print( " No constants to apply this universal rule to ")
        if existential:
            sent = transform_existential(sentence_df)
        else:
            sent = transform_universal(sentence_df)
        return [sent]

    

    somebody_everybody = False
    for_object = False
    if existential:
        existentials = sentence_df.loc[0, "Existential quantifier"].split()
    else:
        existentials = sentence_df.loc[0, "Universal quantifier"].split()

    
    
    subject = lemmatize(get_item(sentence_df, "Subject"))
    obj = lemmatize(get_item(sentence_df, "Obj"))
    verb = get_item(sentence_df, "Verb")
    adjective = False
    if len(subject.split())>1:
        adjective = True
        subjects = subject.split()

    verb_lemma = ""
    doc = nlp(verb)
    for token in doc:
        verb_lemma = token.lemma_
    if verb_lemma == "be" and obj == "":
        obj = sentence_split[int(sentence_df.loc[0, "Verb"])+1]
        doc = nlp(or_sentence)
        for k,tok in enumerate(doc):
            if k ==int(sentence_df.loc[0, "Verb"])+1 and (tok.dep_ == "det" or tok.pos_ == "DET") :        
                obj = sentence_split[int(sentence_df.loc[0, "Verb"])+2]

    
    

    if existentials[1] == "obj": 
        for_object = True 
        if int(existentials[0]) == int(sentence_df.loc[0, "Obj"]): # Mary hates everyone
            somebody_everybody = True
    elif int(existentials[0]) == int(sentence_df.loc[0, "Subject"]): # Everyone hates Mary
        somebody_everybody = True

    last_part = ""
    verb_indices =  [int(c) for c in sentence_df.loc[0, "Verb"]]
    verb_index = verb_indices[len(verb_indices) - 1]
    for i,s in enumerate(sentence_split):
        if i > verb_index:
            last_part += " "+s

    new_sentence = ""
    statements = []
  
    # Mary hates everyone -> somebody_everybody, for_object

    # Mary hates all humans -> for_object

    if not for_object:

        for key in keys:
            if somebody_everybody:
                if verb_lemma == "be":
                    new_sentence = f"{key} is {last_part}" # Everyone is ...
                elif obj != "":
                    new_sentence = f"{key} {verb} {last_part}" #Everyone hates ...
                else: 
                    new_sentence = f"{key} {verb}" # Everyone eats
            
            elif existential:    

                if adjective: # some heavy fish are gray

                    if verb_lemma == "be":
                        new_sentence = f"{key} is {subjects[0]} and {key} is {subjects[1]} and {key} is {last_part}" # Some tall humans are mortal
                    elif obj != "":
                        new_sentence = f"{key} is {subjects[0]} and {key} is {subjects[1]} and {key} {verb} {last_part}" #Some tall humans hate ...
                    else: 
                        new_sentence = f"{key} is {subjects[0]} and {key} is {subjects[1]} and {key} {verb}" #Some tall human eat

                else:
                    if verb_lemma == "be":
                        new_sentence = f"{key} is {subject} and {key} is {last_part}" # Some humans are mortal
                    elif obj != "":
                        new_sentence = f"{key} is {subject}  and {key} {verb} {last_part}" #Some humans hate ...
                    else: 
                        new_sentence = f"{key} is {subject} and {key} {verb}" #Some human eat
            else:
                if adjective: # all heavy fish are gray
                    if verb_lemma == "be":
                        new_sentence = f"if {key} is {subjects[0]} and {key} is {subjects[1]} then {key} is {last_part}" # All humans are mortals
                    elif obj != "":
                        new_sentence = f"if {key} is {subjects[0]} and {key} is {subjects[1]} then {key} {verb} {last_part}" # All humans hate ...
                    else: 
                        new_sentence = f"if {key} is {subjects[0]} and {key} is {subjects[1]} then {key} {verb}" # All humans eat
                else:
                    if verb_lemma == "be":
                        new_sentence = f"if {key} is {subject} then {key} is {last_part}" # All tall humans are mortals
                    elif obj != "":
                        new_sentence = f"if {key} is {subject} then {key} {verb} {last_part}" # All humans hate ...
                    else: 
                        new_sentence = f"if {key} is {subject} then {key} {verb}" # All humans eat
            statements.append(new_sentence)

    else:
        for key in keys:
            if somebody_everybody:
                if verb_lemma == "be":
                    new_sentence = f"{subject} is {key}" # Mary is everyone
                elif obj != "":
                    new_sentence = f"{subject} {verb} {key}" # Mary hates everyone
                         
            elif existential:            
                
                if verb_lemma == "be":
                    new_sentence = f"{key} is {obj} and {subject} is {obj}" # Mary is some human
                elif obj != "":
                    new_sentence = f"{key} is {obj} and {subject} {verb} {obj}" # Mary hates some humans
                
            else:
                if verb_lemma == "be":
                    new_sentence = f"if {key} is {obj} then {subject} is {key}" # Mary is every human
                elif obj != "":
                    new_sentence = f"if {key} is {obj} then {subject} {verb} {key}" # Mary hates every human
                
            statements.append(new_sentence)

    
   

    return statements


def solve_final_exi_uni(root):
    leaves = get_leaves(root)
    stop = False
    new_true = []
    new_false = []
    parent_sentence = ""
    highlighted_parts = []
    rule = 20
    for leaf in leaves:
        if leaf.value["Contradiction"].iloc[0] == False:
            leaf.clean_dataframe()
            true_part = leaf.value["True Statements"].iloc[0]
            false_part = leaf.value["False Statements"].iloc[0]

            if isinstance(true_part, str):
                true_part = [true_part]

            if isinstance(false_part, str):
                false_part = [false_part]

            if len(true_part) > 0:
                
                for item in true_part:
                    sentence_df = text_label(item)
                    if sentence_df.loc[0, "Height"] == 5 and sentence_df.loc[0, "Universal quantifier"] != "":
                        if not stop:
                            parent_sentence = item
                            rule = 9
                            new_sentence = add_all_variables(sentence_df, False)
                            new_part = true_part.copy()
                            new_part.remove(item)
                            for s in new_sentence:
                                new_part.append(s)
                                highlighted_parts.append(s)
                            new_true = new_part
                            new_false = false_part
                            unfinished_leaf = leaf
                            stop = True
                        else:
                            leaf.value["End"].iloc[0] = False            
            if len(false_part) > 0:
                for item in false_part:
                    sentence_df = text_label(item)
                    
                    if sentence_df.loc[0, "Height"] == 5 and sentence_df.loc[0, "Existential quantifier"] != "":
                        
                        if not stop:
                            rule = 12
                            new_sentence = add_all_variables(sentence_df, True)
                            parent_sentence = item
                            new_part = false_part.copy()
                            new_part.remove(item)
                            for s in new_sentence:
                                new_part.append(s)
                                highlighted_parts.append(s)
                            new_true = true_part
                            new_false = new_part
                            unfinished_leaf = leaf
                            stop = True
                        else:
                            leaf.value["End"].iloc[0] = False

    if stop:        
        df_child = pd.DataFrame({
            'True Statements': [new_true],
            'False Statements': [new_false],
            'End': [False],
            'Contradiction': [False],
            'Rule': [rule],
            'Highlight': [highlighted_parts],
            'Parent': [parent_sentence]
            })
        

        child_node = TreeNode(df_child)
        unfinished_leaf.add_child(child_node)

    solve_tree(root)



def solve_tree(root):
    
    iteration_count = 0
    final_operation = False
    while True: 

        leaves = get_leaves(root)

        if all(leaf.value["Contradiction"].iloc[0] for leaf in leaves):
            return True
        
        if all(leaf.value["End"].iloc[0] for leaf in leaves):
            break  
        
        
        for leaf in leaves:
            leaf.clean_dataframe()
            
            updated = False
            one_side_done = False

            if leaf.value["End"].iloc[0] == False or leaf.value["Contradiction"].iloc[0] == False:  #only checking nodes that are not "finished" yet
                
                true_part = leaf.value["True Statements"].iloc[0]
                false_part = leaf.value["False Statements"].iloc[0]

                past_true = []
                past_false = []

                if len(true_part) > 0:

                    sign = 1
                    stop = False

                    if isinstance(true_part, list): #if it's a list, multiple sentences are in it and i need to iterate through them

                        for item in true_part:
                            if not stop:
                                sentence_df = text_label(item)

                                if sentence_df.loc[0, "Height"] == 5 and sentence_df.loc[0, "Not operator"] == "" and sentence_df.loc[0, "Existential quantifier"] == "":

                                    if sentence_df.loc[0, "Universal quantifier"] != "":
                                            final_operation = True
                               
                                    #TODO uni and exi

                                    past_true.append(item)
                                    continue

                                solve_sentence(item, leaf, sign)
                                updated = True
                                stop = True
                            else:
                                past_true.append(item)
                        if updated == False:
                            one_side_done = True
                            if len(false_part)<1:
                                leaf.value.loc[0, "End"] = True 

                    elif isinstance(true_part, str): #if it's a string, no need to iterate

                        sentence_df = text_label(true_part)
                        if sentence_df.loc[0, "Height"] == 5 and sentence_df.loc[0, "Not operator"] == "" and sentence_df.loc[0, "Existential quantifier"] == "":
                            if sentence_df.loc[0, "Universal quantifier"] != "":
                                    final_operation = True
                            
                            one_side_done = True
                            past_true.append(true_part)
                            if len(false_part)<1:
                                leaf.value.loc[0, "End"] = True 
                        else:                            
                            solve_sentence(true_part, leaf, sign)
                            updated = True

                if len(false_part) > 0:
                    sign = -1
                    stop = False
                    if isinstance(false_part, list):
                        for item in false_part:
                            if not stop and not updated: 
                                sentence_df = text_label(item)
                                if sentence_df.loc[0, "Height"] == 5 and sentence_df.loc[0, "Not operator"] == "" and sentence_df.loc[0, "Universal quantifier"] == "" :
                                    if sentence_df.loc[0, "Existential quantifier"] != "":
                                            final_operation = True
                                    past_false.append(item)
                                    continue
                                solve_sentence(item, leaf, sign)
                                stop = True
                                updated = True
                            else:
                                past_false.append(item)
                        if updated == False:
                            if len(true_part)<1 or one_side_done:
                                leaf.value.loc[0, "End"] = True 
                    elif isinstance(false_part, str): 
                        
                        if not updated:
                            sentence_df = text_label(false_part)
                            if sentence_df.loc[0, "Height"] == 5 and sentence_df.loc[0, "Not operator"] == "" and sentence_df.loc[0, "Universal quantifier"] == "":
                                if sentence_df.loc[0, "Existential quantifier"] != "":
                                            final_operation = True
                                if len(true_part)<1 or one_side_done:
                                    leaf.value.loc[0, "End"] = True 
                            else:
                                solve_sentence(false_part, leaf, sign)
                                updated = True
                        else:
                            past_false.append(false_part)
                
                if updated:
                   for child in leaf.children:
                        
                        
                        true_statements = child.value.loc[0, "True Statements"]
                       
                        if isinstance(true_statements, str):
                            true_statements = [true_statements]
                        elif not isinstance(true_statements, list):
                            true_statements = list(true_statements)

                        
                        false_statements = child.value.loc[0, "False Statements"]
                        if isinstance(false_statements, str):
                            false_statements = [false_statements]
                        elif not isinstance(false_statements, list):
                            false_statements = list(false_statements)

                        
                        if isinstance(past_true, str):
                            past_true = [past_true]

                        if len(past_true) > 0:
                            true_statements += past_true  
                            child.value.at[0, "True Statements"] = true_statements

                       
                        if isinstance(past_false, str):
                            past_false = [past_false]

                        if len(past_false) > 0:
                            false_statements += past_false 
                            child.value.at[0, "False Statements"] = false_statements
                        
                        boolean,tp,fp = find_contradictions(child)
                        child.value.at[0, "Contradiction"] = boolean
                        child.value.at[0, "End"] = boolean
                        if boolean:
                            child.value.at[0, "True Contradiction"] = tp
                            child.value.at[0, "False Contradiction"] = fp
                        child.clean_dataframe()
                
                
        iteration_count += 1
        
        # iteration limit 
        if iteration_count >= 100:
            print(f"Iteration limit of {100} reached.")
            return False
    
    #HERE I NEED TO CHECK FOR FINAL EXISTENTIAL AND UNIVERSAL

    if final_operation:
        solve_final_exi_uni(root)

    leaves = get_leaves(root)
    all_contradictions = True
    for leaf in leaves:
        if leaf.value["End"].iloc[0]:
            boolean, tp, fp = find_contradictions(leaf)
            leaf.value.at[0, "Contradiction"] = boolean
            if boolean:
                leaf.value.at[0, "True Contradiction"] = tp
                leaf.value.at[0, "False Contradiction"] = fp
            if not boolean:
                all_contradictions = False
    return all_contradictions



#if I have initial sentence that contains a proper noun, I want to save it as a constant for possible future use
def save_constants(text):
    doc = nlp(text)
    global constants_df
    for token in doc:
        if token.pos_ == "PROPN" :
            if token.text not in constants_df["key"].values:
            
                constants_df = pd.concat(
                    [constants_df, pd.DataFrame({"key": [token.text], "value": [""]})],
                    ignore_index=True
                )
        elif token.pos_ == "PRON" and token.text in {"I", "you"} :
            if token.text not in constants_df["key"].values:
            
                constants_df = pd.concat(
                    [constants_df, pd.DataFrame({"key": [token.text], "value": [""]})],
                    ignore_index=True
                )
                   

def make_tree(sentence, sign): #TODO check if right
    data1 = {
        "key": [],
        "value": []
    }


    data2 = {
        "key": [
            "Alice", "Brian", "Catherine", "David", "Emma", "Frank", "Grace",
            "Hannah", "Isaac", "Jack", "Katherine", "Liam", "Mia", "Nathan",
            "Olivia", "Paul", "Quinn", "Rachel", "Sophia", "Thomas", "Uma",
            "Victor", "William", "Xander", "Yasmine", "Zachary"
        ],
        "value": [""] * 26 
    }

    global constants_df
    constants_df = pd.DataFrame(data1)
    global variables_df
    variables_df = pd.DataFrame(data2)
    save_constants(sentence)
    index = 0

    if sign <0:
        df_root = pd.DataFrame({
            'True Statements': [""],
            'False Statements': [sentence],
            'End': [False],
            'Contradiction': [False],
            'Rule': [0],
            'Highlight': [""],
            'Parent': [""]
            })
            
        
        root = TreeNode(df_root)
    else:
        df_root = pd.DataFrame({
            'True Statements': [sentence],
            'False Statements': [""],
            'End': [False],
            'Contradiction': [False],
            'Rule': [0],
            'Highlight': [""],
            'Parent': [""]
            })
        root = TreeNode(df_root)
    
    print(constants_df)
    boolean = solve_tree(root)
    
    return root, boolean

def make_tree_inference(statements, conclusions):

    data1 = {
        "key": [],
        "value": []
    }


    data2 = {
        "key": [
            "Alice", "Brian", "Catherine", "David", "Emma", "Frank", "Grace",
            "Hannah", "Isaac", "Jack", "Katherine", "Liam", "Mia", "Nathan",
            "Olivia", "Paul", "Quinn", "Rachel", "Sophia", "Thomas", "Uma",
            "Victor", "William", "Xander", "Yasmine", "Zachary"
        ],
        "value": [""] * 26 
    }

    global constants_df
    constants_df = pd.DataFrame(data1)
    global variables_df
    variables_df = pd.DataFrame(data2)
    index = 0
    save_constants(statements)
    save_constants(conclusions)
    

    df_root = pd.DataFrame({
        'True Statements': [statements],
        'False Statements': [conclusions],
        'End': [False],
        'Contradiction': [False],
            'Rule': [0],
            'Highlight': [""],
            'Parent': [""]
            })
    root = TreeNode(df_root)
    
    
    boolean = solve_tree(root)
    
    return root, boolean


def make_tree_inference_defe(statements, conclusions, extra_statement):

    data1 = {
        "key": [],
        "value": []
    }


    data2 = {
        "key": [
            "Alice", "Brian", "Catherine", "David", "Emma", "Frank", "Grace",
            "Hannah", "Isaac", "Jack", "Katherine", "Liam", "Mia", "Nathan",
            "Olivia", "Paul", "Quinn", "Rachel", "Sophia", "Thomas", "Uma",
            "Victor", "William", "Xander", "Yasmine", "Zachary"
        ],
        "value": [""] * 26 
    }

    global constants_df
    constants_df = pd.DataFrame(data1)
    global variables_df
    variables_df = pd.DataFrame(data2)
    index = 0

    if isinstance(statements,list):
        for s in statements:
            save_constants(s)
    else:
        save_constants(statements)
    if isinstance(conclusions,list):
        for s in conclusions:
            save_constants(s)
    else:
        save_constants(conclusions)
    

    df_root = pd.DataFrame({
        'True Statements': [statements],
        'False Statements': [conclusions],
        'End': [False],
        'Contradiction': [False],
            'Rule': [0],
            'Highlight': [""],
            'Parent': [""],
            'Defeasible': [extra_statement]
            })
    root = TreeNode(df_root)
    
    
    boolean = solve_tree(root)
    
    return root, boolean

