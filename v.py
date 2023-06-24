import os
import random
import time
import psutil
from playsound import playsound
from datetime import datetime
from gtts import gTTS

questions_to_answer=0
questions_answered=0
true_answers=0
false_answers=0



def text_to_speech(text):
    try:
        file=f"mp3\\{text}.mp3".replace(' ','_')
        tts = gTTS(text=text, lang='en')
 #       print (f"file is {file}")
        tts.save(file)
    except:
        print(f"erreur pour {file}")
        return False

    try:
        play_sound(file)
    except:
        print(f"erreur pour {file}")
    os.remove(file)
    return True


def play_sound(file):
    try:
        playsound(file)
    except:
        print(f"error playing {file}")
    return True



# charge un fichier de vocabulaire (fichier TSV, avec le mot anglais en première position, le mot français en deuxième
# et optionellement le nombre de test à réaliser et le nombre d'erreur en troisème et quatrième position
def load_file(file):
    lines={}
    x_voc_dict={}
    count=0
    try:
        h=open(file,"r",encoding="utf-8")
#        h=open(file,"r",encoding="ISO-8859-1")
        lines=h.readlines()
    except:
        print(f"erreur lors de l'ouverture ou de la lecture du fichier {file}")
    finally:
        h.close()
        
    for line in lines:
        voc_line=line.strip().lower()
        if '\t' in voc_line:

# tente le format sur 4 colonnes (avec nombres de test et d'erreur)                       
            try:
                (english,french,test_str,error_str)=voc_line.split('\t') 
                test = int(test_str)
                error= int(error_str)

# si erreur, tente le format sur 2 colonnes                
            except:
                (english,french)=voc_line.split('\t') 
                test=1
                error=0
                pass
            
            english=english.strip()
            french=french.strip()
            x_voc_dict[english] = {'word':french,'test':test,'error':error}
            count+=1    
                
    print(f"{count} mots chargés à partir du fichier {file}")
    return x_voc_dict

# charge tous les fichiers de vocabulaire dans le répertoire dir
def load_files(dir):
    all_voc_dict={}
    for folder,sub_folders,files in os.walk(dir):
        for file in files:
            voc_dict = load_file(os.path.join(folder,file))
            all_voc_dict.update(voc_dict)
    print (f"{len(all_voc_dict.keys())} mots uniques chargés")                    
    return all_voc_dict



# prend une string composée de un ou plusieurs mots séparés par des virgules
# renvoi une liste triée des mots, sans espace et sans virgules
def clean_and_sort_input(string):
    words=string.lower().split(',')
    cleaned=[]
    for word in words:
        cleaned.append(word.strip())
    cleaned.sort()
    return cleaned
    
def answer_too_long(start,end,anwser): 
    length=0
    for word in anwser:
        length += len(word)
    perf = (end - start)/length
#    print (f"perf = {perf}")
    return (perf > 1 )
    

# compare la saisie avec le contenu attendu pour un mot
def test_word(english,french,input_text):

    start_time = time.time()
    answer=clean_and_sort_input(input_text)
    correct_answer = clean_and_sort_input(french)
#    print (f"comparing {answer} with {correct_answer}")
    if answer == correct_answer:
#        print ("bonne réponse !")
        end_time=time.time()
        if answer_too_long(start_time,end_time,answer):
            print (f"mais temps de réponse trop long {round(end_time-start_time,1)} secondes !")
            return False
        return True
    else:
       # print (f"erreur : {answer} n'est pas {correct_answer} ")
        return False
    

# teste le vocabulaire présent dans le dictionnaire    
def test_voc(x_voc_dict):
    global questions_to_answer, questions_answered, true_answers, false_answers
    english_words =list(x_voc_dict.keys());
    random.shuffle(english_words)
    for english in english_words: 
        french = x_voc_dict[english]
        if (french['test'] <= 0):
            continue

        text_to_speech(english)

        input_text=input(f"traduction pour {english} ? ")
        if input_text.lower() == "q":
            return True,x_voc_dict

        result=test_word(english,french['word'],input_text)
        questions_answered = questions_answered + 1        
        if (result == False):
            false_answers+=1
            french['error'] += 1
            french['test'] = int(french['error']*2)
            for i in range(3):
                print (f"{english} se traduit par => {french['word']}")
            print (f"{french['error'] } erreur : le mot {english} sera demandé {french['test']} fois")
        else:    
            true_answers += 1
            french['test'] += -1
            questions_to_answer -= 1
            if ( french['test'] > 0 ):
                print (f"le mot {english} sera encore demandé {french['test']} fois")

        questions_to_answer=0
        for word in list(x_voc_dict.keys()):
            questions_to_answer += x_voc_dict[word]["test"]
        print (f"{questions_answered} réponses données\t encore {questions_to_answer} questions \ttaux de bonnes réponses {int(true_answers*100/questions_answered)}% ")
  
    return False,x_voc_dict
    
    

def save_dict(x_voc_dict):
    file=f"voc\\out\\voc{str(datetime.now())}.txt"
    file=file.replace(':','_').replace(' ','_').replace('-','_')
    print(f"sauvegarde de {file}")
    try:
        count=0
        h=open(file,"w",encoding="utf-8")
        for english,french in x_voc_dict.items():
            if french['test'] > 0:
                line = "\t".join([english,french['word'],str(french['test']),str(french['error'])])+"\n" 
#                print(f"sauvegarde de la ligne {line}")
                h.write(line)
                count+=1
        h.close()
        print(f"{count} lignes écrites")
        return True 
    except:
        print (f"impossible d'ouvrir ou d'écrire dans {file}")   
        return False 




# main

x_voc_dict = load_files("C:\\vmaret\\Python\\voc\\in")
over=False
while (not over):
    end,x_voc_dict = test_voc(x_voc_dict)
    if end:
        save_dict(x_voc_dict)
        over=True
    else:
        over = True 
        for english,french in x_voc_dict.items():
            if french['test']>0:
                over=False        
        if (over):
            print("tous les mots sont connus!")            	