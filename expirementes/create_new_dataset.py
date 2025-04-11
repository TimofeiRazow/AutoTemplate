
import pandas as pd

labels_map = {
    0: "возбуждении исполнительного производства",
    1: "отказе в возбуждении исполнительного производства",
    2: "внесении изменений в ранее вынесенное постановление",
    3: "отмене постановления частного судебного исполнителя",
    4: "участии переводчика в исполнительном производстве",
    5: "участии специалиста в исполнительном производстве",
    6: "привлечении сотрудников или подразделений органов внутренних дел для обеспечения исполнения исполнительных документов",
    7: "приостановлении исполнительного производства",
    8: "возобновлении исполнительного производства",
    9: "прекращении исполнительного производства",
    10: "возвращении исполнительного документа",
    11: "принятии исполнительного документа к своему производству",
    12: "передаче имущества должника",
    13: "передаче арестованного имущества на реализацию",
    14: "обращении взыскания на дебиторскую задолженность",
    15: "обращении взыскания на заработную плату и иные виды доходов",
    16: "определении задолженности",
    17: "распределении взысканных денежных сумм",
    18: "присоединении к взысканию",
    19: "направлении исполнительного документа в ликвидационную комиссию, банкротному управляющему, реабилитационному управляющему",
    20: "отмене мер обеспечения исполнения исполнительного документа",
    21: "возмещении расходов, понесенных при совершении исполнительных действий",
    22: "утверждении сумм оплаты деятельности частного судебного исполнителя",
    23: "запрещении совершать определенные действия",
    24: "задержании транспортного средства и водворении на специальную стоянку",
    25: "изъятии движимого имущества",
    26: "истребовании информации о номерах банковских счетов и наличии денег на них, сведений о характере и стоимости имущества, находящегося в банках, организациях, осуществляющих отдельные виды банковских операций, а также в страховых организациях, и наложении ареста на них",
    27: "наложении ареста на имущество должника",
    28: "обращении взыскания на имущество",
    29: "временном ограничении на выезд лица, являющегося должником",
    30: "приостановлении временного ограничения на выезд лица",
    31: "снятии временного ограничения на выезд лица",
    32: "приводе лица, уклоняющегося от явки к судебному исполнителю",
    33: "изъятии недвижимого имущества",
    34: "изъятии правоустанавливающих документов",
    35: "обращении взыскания на стипендию, пособие по социальному страхованию, при временной нетрудоспособности, пособие по безработице",
    36: "истребовании информации о характере и содержании денежных требований",
    37: "отводе (самоотводе) специалиста, переводчика, судебного исполнителя, помощника частного судебного исполнителя",
    38: "отказе в отводе (самоотводе) специалиста, переводчика, судебного исполнителя, помощника частного судебного исполнителя",
    39: "назначении оценщика по оценке арестованного имущества, оценки имущества должника",
    40: "объявлении должника в розыск"
}


df = pd.read_csv("data.csv")
df["label"] = df["label"].map(labels_map)
df.to_csv("dataset_up2.csv", index=False, encoding="utf-8")

labels_map = {
    0: "возбуждении исполнительного производства",
    1: "отказе в возбуждении исполнительного производства",
    2: "внесении изменений в ранее вынесенное постановление",
    3: "отмене постановления частного судебного исполнителя",
    4: "участии переводчика в исполнительном производстве",
    5: "участии специалиста в исполнительном производстве",
    6: "привлечении сотрудников или подразделений органов внутренних дел для обеспечения исполнения исполнительных документов",
    7: "приостановлении исполнительного производства",
    8: "возобновлении исполнительного производства",
    9: "прекращении исполнительного производства",
    10: "возвращении исполнительного документа",
    11: "принятии исполнительного документа к своему производству",
    12: "передаче имущества должника",
    13: "передаче арестованного имущества на реализацию",
    14: "обращении взыскания на дебиторскую задолженность",
    15: "обращении взыскания на заработную плату и иные виды доходов",
    16: "определении задолженности",
    17: "распределении взысканных денежных сумм",
    18: "присоединении к взысканию",
    19: "направлении исполнительного документа в ликвидационную комиссию, банкротному управляющему, реабилитационному управляющему",
    20: "отмене мер обеспечения исполнения исполнительного документа",
    21: "возмещении расходов, понесенных при совершении исполнительных действий",
    22: "утверждении сумм оплаты деятельности частного судебного исполнителя",
    23: "запрещении совершать определенные действия",
    24: "задержании транспортного средства и водворении на специальную стоянку",
    25: "изъятии движимого имущества",
    26: "истребовании информации о номерах банковских счетов и наличии денег на них, сведений о характере и стоимости имущества, находящегося в банках, организациях, осуществляющих отдельные виды банковских операций, а также в страховых организациях, и наложении ареста на них",
    27: "наложении ареста на имущество должника",
    28: "обращении взыскания на имущество",
    29: "временном ограничении на выезд физического лица, руководителя (исполняющего обязанности) юридического лица, являющегося должником, из Республики Казахстан",
    30: "приостановлении временного ограничения на выезд физического лица, руководителя (исполняющего обязанности) юридического лица, являющегося должником, из Республики Казахстан",
    31: "снятии временного ограничения на выезд физического лица, руководителя (исполняющего обязанности) юридического лица, являющегося должником, из Республики Казахстан",
    32: "приводе лица, уклоняющегося от явки к судебному исполнителю",
    33: "изъятии недвижимого имущества",
    34: "изъятии правоустанавливающих документов",
    35: "обращении взыскания на стипендию, пособие по социальному страхованию, при временной нетрудоспособности, пособие по безработице",
    36: "истребовании информации о характере и содержании денежных требований, и наложении ареста на них",
    37: "отводе (самоотводе) специалиста, переводчика, судебного исполнителя, помощника частного судебного исполнителя",
    38: "отказе в отводе (самоотводе) специалиста, переводчика, судебного исполнителя, помощника частного судебного исполнителя",
    39: "назначении оценщика по оценке арестованного имущества либо поручение о проведении оценки имущества должника одной из сторон исполнительного производства",
    40: "объявлении должника в розыск"
}