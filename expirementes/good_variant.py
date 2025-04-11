from transformers import pipeline
from termcolor import colored
import torch

class Ner_Extractor:
    """
    Labeling each token in sentence as named entity

    :param model_checkpoint: name or path to model 
    :type model_checkpoint: string
    """
    
    def __init__(self, model_checkpoint: str):
        self.token_pred_pipeline = pipeline("token-classification", 
                                            model=model_checkpoint, 
                                            aggregation_strategy="average")
    
    @staticmethod
    def text_color(txt, txt_c="red", txt_hglt="on_yellow"):
        """
        Coloring part of text 
        
        :param txt: part of text from sentence 
        :type txt: string
        :param txt_c: text color  
        :type txt_c: string        
        :param txt_hglt: color of text highlighting  
        :type txt_hglt: string
        :return: string with color labeling
        :rtype: string
        """
        return colored(txt, txt_c, txt_hglt)
    
    @staticmethod
    def concat_entities(ner_result):
        """
        Concatenation entities from model output on grouped entities
        
        :param ner_result: output from model pipeline 
        :type ner_result: list
        :return: list of grouped entities with start - end position in text
        :rtype: list
        """
        entities = []
        prev_entity = None
        prev_end = 0
        for i in range(len(ner_result)):
            
            if (ner_result[i]["entity_group"] == prev_entity) &\
               (ner_result[i]["start"] == prev_end):
                
                entities[i-1][2] = ner_result[i]["end"]
                prev_entity = ner_result[i]["entity_group"]
                prev_end = ner_result[i]["end"]
            else:
                entities.append([ner_result[i]["entity_group"], 
                                 ner_result[i]["start"], 
                                 ner_result[i]["end"]])
                prev_entity = ner_result[i]["entity_group"]
                prev_end = ner_result[i]["end"]
        
        return entities
    
    
    def colored_text(self, text: str, entities: list):
        """
        Highlighting in the text named entities
        
        :param text: sentence or a part of corpus
        :type text: string
        :param entities: concated entities on groups with start - end position in text
        :type entities: list
        :return: Highlighted sentence
        :rtype: string
        """
        colored_text = ""
        init_pos = 0
        result = []
        for ent in entities:
            if ent[1] > init_pos:
                colored_text += text[init_pos: ent[1]]
                colored_text += self.text_color(text[ent[1]: ent[2]]) + f"({ent[0]})"
                init_pos = ent[2]
            else:
                colored_text += self.text_color(text[ent[1]: ent[2]]) + f"({ent[0]})"
                init_pos = ent[2]
        
        return colored_text
    
    
    def get_entities(self, text: str):
        """
        Extracting entities from text with them position in text
        
        :param text: input sentence for preparing
        :type text: string
        :return: list with entities from text
        :rtype: list
        """
        assert len(text) > 0, text
        entities = self.token_pred_pipeline(text)
        print(entities)
        concat_ent = self.concat_entities(entities)
        
        return concat_ent
    
    
    def show_ents_on_text(self, text: str):
        """
        Highlighting named entities in input text 
        
        :param text: input sentence for preparing
        :type text: string
        :return: Highlighting text
        :rtype: string
        """
        assert len(text) > 0, text
        entities = self.get_entities(text)
        
        return self.colored_text(text, entities)

seqs_example = ["""ПОСТАНОВЛЕНИЕ о возбуждении исполнительного производства 12.03.2022	г. Алматы Алматинская область """,
                """Частный судебный исполнитель исполнительного округа Алматинского округа Алматинская область, г. Алматы, ул. Мусрепов 8, """,
                """Иванов Иван Иванович рассмотрев Ст. 9 п. 11-1. исполнительная надпись; №2345785777098 от 12.03.2022 года о взыскании 150000 тенге """
                """(взыскатель ТОО "Каз Трейд" 43256745375 БИН, должник Разов Тимофей Дмитриевич 345698676890 ИИН) поступившего 03.04.2022 года из Суд города Алматы"""
               ]

extractor = Ner_Extractor(model_checkpoint = "surdan/LaBSE_ner_nerel")

show_entities_in_text = (extractor.show_ents_on_text(i) for i in seqs_example)
result = []
for text in seqs_example:
    for entity in extractor.get_entities(text):
        result.append((entity[0], text[entity[1] : entity[2]]))
print(result)
l_entities = [[{i[j[1] : j[2]] : j[0] } for j in extractor.get_entities(i)] for i in seqs_example]
len(l_entities), len(seqs_example)


for i in range(len(seqs_example)):
    print(next(show_entities_in_text, "End of generator"))
    print("-*-"*25)