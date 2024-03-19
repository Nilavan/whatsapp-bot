from flask import Flask, request, session
from twilio.rest import Client
import asyncio
from rasa.core.agent import Agent
from rasa.shared.utils.io import json_to_string
import os
import urllib
# import pandas as pd

greetings = ['hello', 'sasa', 'habari', 'aloha', 'jambo', 'uko', 'aje', 'habari yako', 'hi', 'hey', 'help', 'how are you', 'uko fiti', 'uko poa', 'habari ya asubuhi', 'good morning', 'morning', 'good evening', 'good afternoon']

introduction = [
    "👋 Hi! I'm Lydia, your virtual assistant for DiRP - the app dedicated to reporting positive or negative social and environmental issues in your community. Our goal is to ensure timely response from relevant authorities, addressing concerns swiftly. By sharing positive stories, we aim to inspire others, fostering unity and the spirit of 'Leave no one behind'. 🌍",
    "👋 Salama! Mimi ni Lydia, msaidizi wako wa kielektroniki kwa DiRP - programu iliyolenga kuripoti masuala chanya au hasi ya kijamii na kimazingira katika jamii yako. Lengo letu ni kuhakikisha majibu ya wakati kutoka kwa mamlaka husika, kushughulikia masuala kwa haraka. Kwa kushiriki hadithi chanya, lengo letu ni kuhamasisha wengine, kukuza umoja na roho ya 'Usiache yeyote nyuma'. 🌍",
    "👋 Ĩngwene! Ūrīa wakwa nū Lydia, rīūrī rīa ūtūka-inī kwa DiRP - irīa ūhingo wa kūrīo ūnū nūci-inī tūhīūka mūrīrī wa mūci-inī wa ūhandū na ūkahenio-inī ūra wa thīnaga. Ūrahūīna rīa thūngū kūrīa gūkena maīri-inī mūrīaga kūrīona, rīherereira nūthīūna-inī kūrī mwega nūciī, ūtūhīūka wa mwega nūcī na rūrīrī wa 'Mwene ūheni mahūngū'. 🌍"
]

main_menu = [
    "Please choose what you'd like to do:\n1. 📱 How to report social and environmental incidents from your phone\n2. 🌍 Learn about various social and environmental incidents happening around you.\n3. 🚫 Find out how to counter mis and disinformation effectively.\n4. ℹ️ Get information on various initiatives happening in your community and how you can contribute to change",
    "Tafadhali chagua unachotaka kufanya:\n1. 📱 Jinsi ya kuripoti matukio ya kijamii na mazingira kupitia simu yako\n2. 🌍 Jifunze kuhusu matukio mbalimbali ya kijamii na mazingira yanayotokea karibu yako\n3. 🚫 Pata habari jinsi ya kupinga habari za uongo na ufinyo wa taarifa kwa ufanisi\n4. ℹ️ Pata taarifa kuhusu miradi mbalimbali inayoendelea katika jamii yako na jinsi unavyoweza kuchangia kuleta mabadiliko",
    "Thandika ta iria unaiitíirie kúhíra:\n1. 📱 Thathathara iria ya kúgiigiriria mithukiri ya ciana na iria na maitumere magúkúrú-iníria\n2. 🌍 Hingĩka-inírie núkúkúrĩra maithukire maúma maúmwoya na iria-iní maraini\n3. 🚫 Thathathara tene-iníria ĩmũta wa kúgeria kúrihúra-ini na iria ĩngenĩ-iníria\n4. ℹ️ Ĩingĩkire maithukire-iní guandúrwo na matarĩriĩ maúma maraini-iní kwigikĩra ũkũmbĩra gĩkĩ"
]

download_app_confirm = [
    "Would you like to download the 'DiRP' app? (yes/no): ", 
    "Ungependa kupakua programu ya 'DiRP'? (ndiyo/hapana): ", 
    "Wendete gukata na kurithira app ya 'DiRP'? (eee/apana): "
] 

anything_else_dialog = [
    "Is there anything else I can assist you with? (yes/no)",
    "Kuna kitu kingine naweza kukusaidia nacho? (ndiyo/hapana)",
    "Niathi cia arumenya andu niundithirie? (eee/apana)"
]

incident_confirm = [
    "I'm here to assist! To understand the situation better, can you tell me more about what you've encountered 🕵️‍♂️",
    "Nipo hapa kusaidia! Ili kuelewa hali vizuri, unaweza kunielezea zaidi kuhusu uliyokumbana nayo? 🕵️‍♂️",
    "Nguicio ni tùguo! Ûhoro wakù nì gùkorwo, hagwo nìù ngūkùrana na magùkù mùno wa ûrìkù. 🕵️‍♂️"
]

app_steps = [
    "Here are the steps to report social and environmental incidents from the DiRP app: \n1. 📱 Open the DiRP app on your mobile device. \n2. 🖊️ Sign in to your account or create a new account if you haven't already. \n3. 🚀 Navigate to the 'Report Incident' or 'Submit Report' section within the app. \n4. 🌳 Choose the category or type of incident you want to report (e.g., pollution, wildlife poaching, forest fire). \n5. ℹ️ Provide detailed information about the incident, including the location, date, and description. \n6. 📸 If possible, upload any relevant photos or videos as evidence of the incident. \n7. 🔍 Review the information you've provided to ensure accuracy and completeness. \n8. ✉️ Submit the report by tapping the 'Submit' or 'Send' button. \n9. ⏳ Wait for confirmation that your report has been received and processed by the DiRP team. \n10. 🔄 Optionally, you may receive updates on the status of your report and any actions taken by authorities to address the incident. \n\nThese steps will help you effectively report social and environmental incidents using the DiRP app.",
    "Hizi ni hatua za kuripoti matukio ya kijamii na mazingira kutumia programu ya DiRP: \n1. 📱 Fungua programu ya DiRP kwenye kifaa chako cha simu. \n2. 🖊️ Ingia kwenye akaunti yako au jisajili kwa akaunti mpya ikiwa hujafanya hivyo tayari. \n3. 🚀 Naviga kwenye sehemu ya 'Ripoti Tukio' au 'Tuma Ripoti' ndani ya programu. \n4. 🌳 Chagua jamii au aina ya tukio unayotaka kuripoti (k.m., uchafuzi, ujangili wa wanyamapori, moto wa misitu). \n5. ℹ️ Toa maelezo ya kina kuhusu tukio, ikiwa ni pamoja na eneo, tarehe, na maelezo. \n6. 📸 Ikiwa inawezekana, pakia picha au video zinazohusiana kama ushahidi wa tukio. \n7. 🔍 Hakiki maelezo uliyotoa ili kuhakikisha usahihi na ukamilifu. \n8. ✉️ Tuma ripoti kwa kubonyeza kitufe cha 'Tuma' au 'Send'. \n9. ⏳ Subiri uthibitisho kwamba ripoti yako imepokelewa na kusindika na timu ya DiRP. \n10. 🔄 Hiari, unaweza kupokea sasisho kuhusu hali ya ripoti yako na hatua zozote zilizochukuliwa na mamlaka kushughulikia tukio. \n\nHatua hizi zitakusaidia kuripoti matukio ya kijamii na mazingira kwa ufanisi kutumia programu ya DiRP.",
    "Nduhî îci mûrîkûna kûgûî kîrîma kûrîa mîndûrî yo kîîrutwo nî mûrîrîa wa DiRP: \n1. 📱 Îndûrîrwo ûrî wa DiRP mûngîkû kûînjahûkûrûrûrû. \n2. 🖊️ Jîrînyûrwo ûrî mûmbârîyo mûkarîng'ûrîra nîkâbât'ûrîrwo kîrîîrwo nî mûrîûrî nî kûrîtwa njû mûthâ. \n3. 🚀 Jîûkûmâ kînjûkîrwo nî 'Rîpôtî Tûkîû' ûrî 'Tûmâ Rîpôtî' nîcîcî wa mûrîrîa. \n4. 🌳 Jûûrîrwo jîrîcî nî îrîrwo nî mûrîûrî nî ûrî wîndûrîra (gî, ûkâpûrî, ûjûng'êrî wa ûnîyâ, ûmjîû wa mîrûrû). \n5. ℹ️ Tûmûrwo mûrîî nîgûka kûkîcî nîcîndîkî, îrîêgâ ûrî, nî îrîînjîkî. \n6. 📸 Iwûûrwo nîndûrîra nînâîgârî, mûrîga nî mûbîthî îû rînîyâkûkû. \n7. 🔍 Rîînâgâ mûrîî îrîîndûrîa ûrî îwînjîgîra ûsâhîrî nî nîhûgîrî. \n8. ✉️ Tûmâ rîpôtî kîbârî nî nîgûtûrwo kîhûrîrî cîthîû. \n9. ⏳ Gûgûkî njêgûkîrwo nîgûcîgûrî kîrîpôtî yûrî nîgûhûgîrîrwo nî njêgûkî rîîrwo îriîsû nî ûmwîmû wa DiRP. \n10. 🔄 Thûûwî, ûnâûrwo kûrîdîkûkû kûrîpôtî yûrî nî ûhâtîrîrwo kîhâtîrî wa njêgûkî."
]

download_app_steps = [
    "To download the 'DIRP' app, follow these steps:\n1. Go to the App Store or Google Play Store.\n2. Search for 'DIRP'.\n3. Download and install the app.\n4. You can find more information and download the app from [here](link_to_app).",
    "Kupakua programu ya 'DIRP', fuata hatua hizi:\n1. Nenda kwa Duka la App au Duka la Google Play.\n2. Tafuta 'DIRP'.\n3. Pakua na usakinishe programu.\n4. Unaweza kupata maelezo zaidi na kupakua programu kutoka [hapa](link_to_app).",
    "Kurithira app ya 'DIRP', gukaria mwomboko mugiko:\n1. Ota kwa Duka ria Riari kana Duka ria Google Play.\n2. Turagia 'DIRP'.\n3. Rithira na ugorithirie app.\n4. Wendete kurathira maitumere na kwathira app kwa [hapa](link_to_app)."
]

misinformation_confirm = [
    "Would you like information on a specific type of digital misinformation? (yes/no)",
    "Ungependa maelezo kuhusu aina fulani ya habari za uongo mtandaoni? (ndiyo/hapana)",
    "Ungekùcia mathathi na iria cia hiakúí maruteire? (eee/apana)"
]

counter_misinformation_guide = [
    "In the modern digital era, combatting misinformation and disinformation is crucial. It involves critically evaluating information sources, fact-checking, and verifying before sharing. Encouraging media literacy and promoting critical thinking skills are essential. By staying vigilant and responsible online, we can mitigate the spread of false information and uphold the integrity of information dissemination.",
    "Katika enzi ya kidijitali ya kisasa, kupambana na habari potofu na upotoshaji ni muhimu. Hii inahusisha kutathmini kwa kina vyanzo vya habari, kufanya uhakiki wa ukweli, na kuthibitisha kabla ya kushiriki. Kuhamasisha elimu ya vyombo vya habari na kukuza uwezo wa kufikiri kwa kina ni muhimu. Kwa kubaki macho na kuwa na uwajibikaji mtandaoni, tunaweza kupunguza kuenea kwa habari za uongo na kudumisha uadilifu wa usambazaji wa habari.",
    "Mũtumĩkĩrĩrwo wa mũceke wa ciana na ĩmbíro-inĩ mũgĩĩka ni mũhĩrĩrĩkĩrie. Ĩno ĩrĩa gũrũkĩra ĩtangi ĩngiĩ-inĩ na iga-inĩ, kũongera kwĩtiga na kũndĩkĩrĩra kũhũma kwĩga na kwĩrĩa. Ĩtiga mũndũ-kũta ndĩthuha wa rũrĩri na kũhũma mũhĩrĩa wa kwĩga kũrĩrĩa ĩkĩnda. Nĩ gũmba na kwĩhĩkĩa mbere-inĩ, thĩnaga twĩhĩkĩira kwĩhĩndĩrĩra ĩndĩmĩra ya ĩkĩmũte no nyũmba wa ũndũri wa ĩkĩnda."
]

misinformation_details_dialog = [
    "Could you please describe the type of digital misinformation you're interested in?",
    "Tafadhali, unaweza eleza aina ya habari za uongo mtandaoni unayopendezwa nayo?",
    "Wandurakìtio, wega undúruka mùgùtì wa hiakúí maruteire unìngùkìria?"
]

locations_list = [
    "To get started, please tell me your general location: \n1. Mombasa\n2. Kwale\n3. Kilifi\n4. Tana River\n5. Lamu\n6. Taita/Taveta\n7. Garissa\n8. Wajir\n9. Mandera\n10. Marsabit\n11. Isiolo\n12. Meru\n13. Tharaka-Nithi\n14. Embu\n15. Kitui\n16. Machakos\n17. Makueni\n18. Nyandarua\n19. Nyeri\n20. Kirinyaga\n21. Murang'a\n22. Kiambu\n23. Turkana\n24. West Pokot\n25. Samburu\n26. Trans Nzoia\n27. Uasin Gishu\n28. Elgeyo/Marakwet\n29. Nandi\n30. Baringo\n31. Laikipia\n32. Nakuru\n33. Narok\n34. Kajiado\n35. Kericho\n36. Bomet\n37. Kakamega\n38. Vihiga\n39. Bungoma\n40. Busia\n41. Siaya\n42. Kisumu\n43. Homa Bay\n44. Migori\n45. Kisii\n46. Nyamira\n47. Nairobi City",
    "Ili kuanza, tafadhali niambie mahali pako kwa ujumla: \n1. Mombasa\n2. Kwale\n3. Kilifi\n4. Tana River\n5. Lamu\n6. Taita/Taveta\n7. Garissa\n8. Wajir\n9. Mandera\n10. Marsabit\n11. Isiolo\n12. Meru\n13. Tharaka-Nithi\n14. Embu\n15. Kitui\n16. Machakos\n17. Makueni\n18. Nyandarua\n19. Nyeri\n20. Kirinyaga\n21. Murang'a\n22. Kiambu\n23. Turkana\n24. West Pokot\n25. Samburu\n26. Trans Nzoia\n27. Uasin Gishu\n28. Elgeyo/Marakwet\n29. Nandi\n30. Baringo\n31. Laikipia\n32. Nakuru\n33. Narok\n34. Kajiado\n35. Kericho\n36. Bomet\n37. Kakamega\n38. Vihiga\n39. Bungoma\n40. Busia\n41. Siaya\n42. Kisumu\n43. Homa Bay\n44. Migori\n45. Kisii\n46. Nyamira\n47. Nairobi City",
    "Ûrùte kùngerera, ûmbere ûrùmù rùa mùrùnda waku: \n1. Mombasa\n2. Kwale\n3. Kilifi\n4. Tana River\n5. Lamu\n6. Taita/Taveta\n7. Garissa\n8. Wajir\n9. Mandera\n10. Marsabit\n11. Isiolo\n12. Meru\n13. Tharaka-Nithi\n14. Embu\n15. Kitui\n16. Machakos\n17. Makueni\n18. Nyandarua\n19. Nyeri\n20. Kirinyaga\n21. Murang'a\n22. Kiambu\n23. Turkana\n24. West Pokot\n25. Samburu\n26. Trans Nzoia\n27. Uasin Gishu\n28. Elgeyo/Marakwet\n29. Nandi\n30. Baringo\n31. Laikipia\n32. Nakuru\n33. Narok\n34. Kajiado\n35. Kericho\n36. Bomet\n37. Kakamega\n38. Vihiga\n39. Bungoma\n40. Busia\n41. Siaya\n42. Kisumu\n43. Homa Bay\n44. Migori\n45. Kisii\n46. Nyamira\n47. Nairobi City"
]

interest_list = [
    "Great! Now, what are you interested in?\n1. 🌳 Tree planting\n2. 🧹 Clean up\n3. 🏪 Market day",
    "Vizuri! Sasa, ungependa kujua kuhusu nini?\n1. 🌳 Upandaji wa miti\n2. 🧹 Usafi wa mazingira\n3. 🏪 Siku ya soko",
    "Mwathani! Ta gĩthĩra, ũkĩagũria kũringanĩ?\n1. 🌳 Kuota mugumo\n2. 🧹 Gũkora na nguo cia mbara\n3. 🏪 Mũthenya wa mwĩrangĩ"
]

interest_details = {
    "1":
        [
            "Interest 1 details go here",
            "Maelezo ya Maslahi 1 yanakwenda hapa",
            "Thutha wa Rúhííru 1 mĩharĩkagĩtū íhara ya mbere ni ĩhagĩkagĩria ĩhĩndĩrĩĩ niĩhĩndĩrĩĩ ici"
        ],
    "2":
        [
            "Interest 2 details go here",
            "Maelezo ya Maslahi 2 yanakwenda hapa",
            "Thutha wa Rúhííru 2 mĩharĩkagĩtū íhara ya mbere ni ĩhagĩkagĩria ĩhĩndĩrĩĩ niĩhĩndĩrĩĩ ici"
        ],
    "3":
        [
            "Interest 3 details go here",
            "Maelezo ya Maslahi 3 yanakwenda hapa",
            "Thutha wa Rúhííru 3 mĩharĩkagĩtū íhara ya mbere ni ĩhagĩkagĩria ĩhĩndĩrĩĩ niĩhĩndĩrĩĩ ici"
        ]
}

goodbye = [
    "Thank you for your time and for using our service! If you have any more questions or need assistance in the future, feel free to reach out by sending a hi. Have a great day ahead! 🌟👋",
    "Asante kwa muda wako na kwa kutumia huduma yetu! Ikiwa una maswali zaidi au unahitaji msaada hapo baadaye, jisikie huru kuwasiliana kwa kutuma ujumbe. Uwe na siku njema! 🌟👋",
    "Ūhoro wa mũhora wako na kūrīa nīgūthambīra ĩrīa rīrīkia! Mūcīa ũhoro wa maithe mīratho nĩmũnene nĩmūkūgūrana kītengū mūrī nĩ gūgūka kārīa. Mūcīaraga tene mūtīe. Ūkūrīre maithe! 🌟👋"
]

incident_guides = {
    "oil_spill":
        [
            "An oil spill is a release of a liquid petroleum hydrocarbon into the environment, especially marine areas, due to human activity. It causes harm to marine life and ecosystems. To learn more about oil spills, you can visit [link_to_resource].",
            "Kumwagika kwa mafuta ni kutolewa kwa hidrokarboni ya mafuta iliyeyuka kwenye mazingira, haswa maeneo ya baharini, kutokana na shughuli za kibinadamu. Inasababisha madhara kwa maisha ya baharini na mifumo ya ikolojia. Ili kujifunza zaidi kuhusu kumwagika kwa mafuta, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Uruma wa mafuta ni kuiganirwo giakwa miruha thabiragia na mafuta macia-ini nyingi maraini, iria gukua miangaza, ngwatiragia iria bururi. Iria gitugia iria gaandu na miti-ini. Ndariha hahingi kuhitugia, wahiha gutuire mai na ciumia-ini nyingi thi [kiugo_kwa_rasilimali]."
        ],
    "forest_fire":
        [
            "A forest fire is an uncontrolled fire occurring in nature, often in forests or wooded areas. It can cause extensive damage to flora, fauna, and habitats. To learn more about forest fires, you can visit [link_to_resource].",
            "Moto wa misitu ni moto usiodhibitiwa unaotokea kiasili, mara nyingi katika misitu au maeneo yenye miti. Inaweza kusababisha uharibifu mkubwa kwa mimea, wanyama, na makazi. Ili kujifunza zaidi kuhusu moto wa misitu, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Moto wa githaka ni moto utanabari ucio ta thakua kihateireiria, gitahi-ini giterereire, nigitekera ciumia na mahuri. Thiikire rui na thangari aandu, miti-ini na miti. Ndariha hahingi kuhitugia, wahiha gutuire mai na ciumia-ini nyingi thi [kiugo_kwa_rasilimali]."
        ],
    "pollution":
        [
            "Pollution is the introduction of harmful or poisonous substances into the environment. It can occur through various human activities such as industrial processes, transportation, and waste disposal. To learn more about pollution, you can visit [link_to_resource].",
            "Uchafuzi ni uingizaji wa vitu vinavyoweza kudhuru au sumu kwenye mazingira. Unaweza kutokea kupitia shughuli mbalimbali za kibinadamu kama vile michakato ya viwanda, usafirishaji, na utupaji wa taka. Ili kujifunza zaidi kuhusu uchafuzi, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Uharibifu ni utungo wa miruru-ini iria-ini itumaga kuomera maraini na macia. Kiumaga kiheteireiria gituma mbau-ini nyingi, niaraguo na miti. Ndariha hahingi kuhitugia, wahiha gutuire mai na ciumia-ini nyingi thi [kiugo_kwa_rasilimali]."
        ],
    "wildlife_poaching":
        [
            "Wildlife poaching is the illegal hunting or capturing of wild animals. It poses a serious threat to biodiversity and can lead to the extinction of endangered species. To learn more about wildlife poaching, you can visit [link_to_resource].",
            "Ujangili wa wanyama pori ni uwindaji au kukamata wanyama pori kinyume cha sheria. Unatishia sana bioanuwai na inaweza kusababisha kutoweka kwa spishi zilizo hatarini. Ili kujifunza zaidi kuhusu ujangili wa wanyama pori, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Uumira wa miruha-ini ni ukiruta-ini na kuriririria iria wanyama wiga. Gaiukaguo niagiririrwo niendete-ini na, miti iria. Ndariha hahingi kuhitugia, wahiha gutuire mai na ciumia-ini nyingi thi [kiugo_kwa_rasilimali]."
        ],
    "climate_change":
        [
            "Climate change refers to long-term shifts in temperature, precipitation, wind patterns, and other aspects of Earth's climate. Causes include human activities such as burning fossil fuels and deforestation. To learn more about climate change, you can visit [link_to_resource].",
            "Mabadiliko ya hali ya hewa yanahusu mabadiliko marefu katika joto, mvua, mifumo ya upepo, na vipengele vingine vya hali ya hewa ya Dunia. Sababu zinazosababisha ni pamoja na shughuli za kibinadamu kama vile kuchoma mafuta ya mafuta na ukataji miti. Ili kujifunza zaidi kuhusu mabadiliko ya hali ya hewa, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Mudirwo-ini wa macia maraini-ini uyu-ini wendete wa kihateireiria waikari wa kihateireiria wa tene mbara na rari-ini miru-ini maraini wa wendete-ini. Ire naiguthi-ini niagira thi ukomaka thi umereireiria wa mbara na mugi. Iu macia ma waiguthagirwo-ini wendete wa wendo thi kurambiriria [kiugo_kwa_rasilimali]."
        ]
}

misinformation_guides = {
    "fake_news":
        [
            "Fake news refers to false information presented as news. It is often spread through social media platforms and websites with the intent to deceive or manipulate readers. To learn more about identifying and combating fake news, you can visit [link_to_resource].",
            "Habari za uongo ni habari za uwongo zilizowasilishwa kama habari. Mara nyingi huzagaa kupitia majukwaa ya media ya kijamii na tovuti zenye nia ya kuwadanganya au kuwashawishi wasomaji. Ili kujifunza zaidi kuhusu kutambua na kupambana na habari za uongo, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Mûratha mîrûa mûndû mûndû kana mûkinya mûkinya waigaga thiîra-inî. Ûkûraruka-inî ûkarînî îrîo ni mîtigîrîra mîkîrîcia kîna mûgîkû yûndû kîena. Ûhûdîndûka-inî mûrûa mûndû-inî ûrîga, ûkûrîa mûndû mûkinya îno ûkûngîrîrîra mîkîrîcia. Niûkûmîrîria thûriî mûndû mûkinya wî, rûtîa mûtûke-inî [kiungo_kwa_rasilimali]."
        ],
    "social_media_rumours":
        [
            "Social media rumors are unverified or false information circulated on social networking platforms. They can spread rapidly and cause panic or misinformation among users. To learn more about identifying and addressing social media rumors, you can visit [link_to_resource].",
            "Uvumi wa media ya kijamii ni habari zisizothibitishwa au za uwongo zinazosambazwa kwenye majukwaa ya kijamii. Wanaweza kusambaa kwa haraka na kusababisha hofu au habari potofu kati ya watumiaji. Ili kujifunza zaidi kuhusu kutambua na kushughulikia uvumi wa media ya kijamii, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Mûratha wa kîrîngû kîrîngû waigaga îmwe mîmwe-inî îmwe mîmwe. Ûkûraruka-inî mûrûa mûndû mûkînî ni cîndûna kana mûrîûngû îno mîgûîra mûndû. Niûkûmîrîria thûriî kîrîngû kîrîngû mûndû, rûtîa mûtûke-inî [kiungo_kwa_rasilimali]."
        ],
    "online_conspiracy_theories":
        [
            "Online conspiracy theories are unfounded or speculative claims that attempt to explain complex events as the result of secret plots by powerful groups. They can undermine trust in institutions and promote paranoia. To learn more about debunking online conspiracy theories, you can visit [link_to_resource].",
            "Tekelezi za nadharia za njama mtandaoni ni madai yasiyothibitishwa au ya kufikirika yanayojaribu kuelezea matukio mazito kama matokeo ya njama za siri na makundi yenye nguvu. Wanaweza kudhoofisha imani katika taasisi na kukuza wazimu. Ili kujifunza zaidi kuhusu kubomoa nadharia za njama mtandaoni, unaweza kutembelea [kiungo_kwa_rasilimali].",
            "Tekeleza waendete wa andu wa ngima kûkû mûthamaki kûkû nûna ndara kîna mûîngû mûîrî. Ûkûraruka-inî mûndû mûthamaki îno ni mîcûku. Niûkûmîrîria thûriî înûmîci waendete wa ngima, rûtîa mûtûke-inî [kiungo_kwa_rasilimali]."
        ]
}

general_misinformation = [
    "Here are some ways to stay safe from misinformation online:\nThink before you share: Take a moment to check the source and credibility of information before forwarding it.\nLook for trusted sources: Rely on websites and social media pages of reputable organizations, news outlets, and government agencies.\nBe cautious of emotional appeals: Don't be swayed by information designed to evoke strong emotions (fear, anger) without providing evidence.\nFact-check suspicious claims: Use independent fact-checking websites or apps to verify information before accepting it as true.\nTalk to others: Discuss information with trusted friends, family, or local community leaders to gain different perspectives.",
    "Hapa kuna njia za kubaki salama dhidi ya habari za uongo mtandaoni:\nTafakari kabla ya kushiriki: Chukua muda wa kuangalia chanzo na uaminifu wa habari kabla ya kuisambaza.\nTafuta vyanzo vinavyoaminika: Tegemea tovuti na kurasa za mitandao ya kijamii za taasisi za kuaminika, vyombo vya habari, na mashirika ya serikali.\nKuwa mwangalifu kwa kuchochea hisia: Usitegwe na habari zinazolenga kuzua hisia kali (hofu, hasira) bila kutoa ushahidi.\nThibitisha madai ya shaka: Tumia tovuti au programu za uhakiki wa ukweli huru kuhakiki habari kabla ya kuiamini kuwa ya kweli.\nZungumza na wengine: Jadiliana habari na marafiki wa kuaminika, familia, au viongozi wa jamii ya kienyeji ili upate mitazamo tofauti.",
    "Mūno ũhoro wa kurangira salama ũrīmwo nî mwanyûmba wa tùhuthagia ũrìkù:\nGĩtwikirie mũkarĩre gũkorĩria: Hĩthūkũ mũkarĩre gũkũmenya mũndũ gũthoma na mũndũo wa wĩndũha mũno mũtumia taundũ nî ngũko inĩ. \nŨmũaga taundũ thĩĩ wĩndĩĩĩ: Nĩgũkũmenya kũhugaga ũrìkù na ũrìkũ wa mũcere, mũkarĩo na makûngũ mũno mũtû wa marĩũngû, mũhurabû, na mũhogo wa gĩthungũ. \nĨgĩkorwo nî gũkorwo: Gũrĩtherera naĩmwe wĩngĩ wa ũrìkù ũîrĩtu wa cioigana-inĩ ngono rĩa (mũroro, mũthanĩ) mũkarĩa tûkwĩa ũndũ wa gũtûkũha gũtigĩria ûrìkù.\nŨmĩra ũmũriĩ wa gĩthũngũ: Mûthamĩrwo thĩinĩ thĩîkwĩaga taundũ ta uhakiki wa ukweli huru mũtûinĩ kũrĩndĩa ũrìkù kũrĩa ũnĩ. \nŨrĩkũrĩka na ûhoro: Gũcûrĩana ûrìkù na maingĩ mwĩngĩ wa ũkarĩre wa wĩngĩ, wakwa, na wakù ûgũrĩa mũcere wa cioigana-inĩ kũîhana mwanyûmba wĩndĩĩĩ."
]

location_welcome = [
    "Welcome to your community information hub. I can help you find out about various initiatives happening in your area and how you can contribute to a sustainable future.",
    "Karibu kwenye kituo chako cha habari za jamii. Nawezakusaidia kupata habari kuhusu miradi mbalimbali inayotokea eneo lako na jinsi unavyoweza kuchangia katika mustakabali endelevu.",
    "Kariani rùrì-inì rwa ìrùa rìa mùrìku. Ndagaagùkanagwo naakùrùa ìhagùko cia mahurùmbì rìaaguo na rìaûkearwo mùcio waku na waiganirie mùndùga."
]

class Model:
    def __init__(self, url: str) -> None:
        target_path = url.split("/")[-1]
        with urllib.request.urlopen(urllib.request.Request(url), timeout=15.0) as response:
            if response.status == 200:
                with open(target_path, "wb") as f:
                    f.write(response.read())
        self.agent = Agent.load(model_path=target_path)
        print("NLU model loaded")

    def message(self, message: str) -> str:
        message = message.strip()
        result = asyncio.run(self.agent.parse_message(message))
        return result['intent']['name']

account_sid = os.environ['twillio_account_sid']
auth_token = os.environ['twillio_auth_token']
client = Client(account_sid, auth_token)

app = Flask(__name__)
app.secret_key = 'oaewedfpioasdofjaposjf'

def send_message(message):
    client.messages.create(to=request.values.get("From"), from_=request.values.get("To"), body=message)

@app.route("/", methods=["POST"])
def bot():
    user_msg = request.values.get('Body', '').lower()
    user_msg = " ".join(user_msg.split()) 
    if 'state' not in session or user_msg in greetings:
        session['state'] = 'start'

    if session['state'] == 'start':
        send_message("👋 Hi there! I'm Lydiah, your helper for reporting positive or negative social and environmental issues happening where you live 🏘️. Our goal is to ensure timely response from relevant authorities, addressing concerns swiftly ⏰. By sharing positive issues happening in your community, we aim to inspire people in other areas, fostering unity and the spirit of 'Leave no one behind' 🌍.")
        session['state'] = "confirm_kenya"
        send_message("Just to let you know, I am designed to work exclusively within Kenya. Could you please confirm that you're currently in Kenya? (yes/no)")
    elif session['state'] == 'confirm_kenya':
        confirm_kenya = user_msg
        if confirm_kenya in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'language_selection'
            send_message('To continue, please choose your preferred language\n1. English\n2. Swahili\n3. Kikuyu')
        else:
            send_message("Apologies, but I don't have information on locations outside Kenya at the moment. If you have any other questions or need further assistance, feel free to ask. Goodbye!")
            session.pop('state', default=None)
        return "Language selection initiated."
    elif session['state'] == 'language_selection':
        language_choice = user_msg
        if language_choice in ['1', '2', '3']:
            session['language'] = int(language_choice)
            session['state'] = 'main_menu'
            send_message(introduction[session['language']-1])
            print(">> Main menu")
            send_message(main_menu[session['language']-1])
        else:
            send_message("Please enter a valid language choice (1, 2, 3).")
        return "Language selected."
    elif session['state'] == 'main_menu':
        menu_choice = user_msg
        if menu_choice in ['1', '2', '3', '4']:
            menu_choice = int(menu_choice)
            session['menu_choice'] = menu_choice
            if menu_choice == 1:
                session['state'] = 'option_1'
                send_message(app_steps[session['language']-1])
                print(">> download app")
                send_message(download_app_confirm[session['language']-1])
            elif menu_choice == 2:
                session['state'] = 'option_2'
                send_message(incident_confirm[session['language']-1])
            elif menu_choice == 3:
                session['state'] = 'option_3'
                send_message(general_misinformation[session['language']-1])
                print(">> misinformation")
                send_message(misinformation_confirm[session['language']-1])
            elif menu_choice == 4:
                session['state'] = 'option_4'
                send_message(location_welcome[session['language']-1])
                print(">> location selection")
                send_message(locations_list[session['language']-1])
        else:
            send_message("Please enter a valid menu choice (1, 2, 3, 4).")
        return "Menu choice selected."
    elif session['state'] == 'option_1':
        download_choice = user_msg
        if download_choice in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'end'
            send_message(download_app_steps[session['language']-1])
        print(">> anything else opt 1")
        session['state'] = "end"
        send_message(anything_else_dialog[session['language']-1])
        return "Option 1 closed"
    elif session['state'] == 'option_2':
        incident_msg = user_msg
        model = Model("https://github.com/Nilavan/whatsapp-bot/raw/main/nlu-20240313-095913-ascent-originator.tar.gz")
        intent = model.message(incident_msg)
        session['state'] = 'end'
        send_message(incident_guides[intent][session['language']-1])
        print(">> anything else opt 2")
        send_message(anything_else_dialog[session['language']-1])
        return "Option 2 closed"
    elif session['state'] == "option_3":
        misinformation_choice = user_msg
        if misinformation_choice in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'option_3_details'
            send_message(misinformation_details_dialog[session['language']-1])
        else:
            session['state'] = "end"
            send_message(anything_else_dialog[session['language']-1])
        return "Option 1 closed"
    elif session['state'] == 'option_3_details':
        misinformation_msg = user_msg
        model = Model("https://github.com/Nilavan/whatsapp-bot/raw/main/nlu-20240318-214623-medium-reflection.tar.gz")
        intent = model.message(misinformation_msg)
        session['state'] = 'end'
        send_message(misinformation_guides[intent][session['language']-1])
        print(">> anything else opt 3")
        send_message(anything_else_dialog[session['language']-1])
        return "Option 2 closed"
    elif session['state'] == 'option_4':
        location_choice = user_msg
        if location_choice in ['1', '2', '3', '4', '5']:
            session['state'] = 'option_4_interest'
            session['location'] = location_choice
            send_message(interest_list[session['language']-1])
        else:
            send_message("Please enter a valid location choice (1, 2, 3, 4, 5).")
        return "Location selected."
    elif session['state'] == 'option_4_interest':
        interest_choice = user_msg
        if interest_choice in ['1', '2', '3']:
            session['state'] = 'end'
            send_message(interest_details[interest_choice][session['language']-1])
            # interest_details = pd.read_csv('')
            # send_message(interest_details[incident_details['location'] == session['location']][incident_details['interest'] == interest_choice])
            session.pop('location', default=None)
            print(">> anything else opt 4")
            send_message(anything_else_dialog[session['language']-1])
        else:
            send_message(f"Please enter a valid interest choice (1, 2, 3)")
    elif session['state'] == 'end':
        anything_else_choice = user_msg
        if anything_else_choice in ['yes', 'ndiyo', 'eee']:
            session['state'] = 'main_menu'
            send_message(main_menu[session['language']-1])
        else:
            send_message(goodbye[session['language']-1])
            session.pop('state', default=None)
        return "Session complete"
    return ""
