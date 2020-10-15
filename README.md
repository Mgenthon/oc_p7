# oc_p7

Le projet est basé sur la compétition Kaggle : https://www.kaggle.com/c/home-credit-default-risk/data. (les datas sont disponibles à cette adresse)
L'idée du projet est d'utiliser les données de Home Credit pour développer un modèle de machine learning capable de prédire le défaut de paiement d'un client.
Ceci afin d'étayer la décision d'accorder ou non un prêt à un client. Après avoir entraîné ce modèle, il faut mettre ce modèle à disposition via une API.

Il faut également développer un dashboard interactif pour que les chargés de relation client puissent expliquer les décisions d’octroi de crédit. Le Dashboard appellera l'API pour avoir le score du client.

Dans le notebook P7_02_Modele, on retrouve le traîtement des donnée (feature engineering) , l'entraînement du modèle, une fonction de coût pour optimiser les profits de Home Credit. On exporte également des données dont on aura besoin pour notre Dashboard.

Dans le dossier api, on retrouve le code pour déployer le modèle de machine learning sous forme d'API (adresse API : https://apiflaskoc.herokuapp.com/).
Les fichiers Procfile et requirements sont utilisés par Heroku et sont indispensables pour le déploiement. Le fichier *.pkl est le modèle entraîné.
L'API renvoie la probabilité de défaut de remboursement entre 0 et 1 (0 = crédit remboursé, 1 = défaut crédit)

Le code pour appeler l'API est le suivant. Il faut fournir à l'API un dictionnaire ayant pour clé les features du fichier features.py (dossier dashboard) et 
les valeurs associés.
url='https://apiflaskoc.herokuapp.com/predict_api'
response = requests.post(url, json=test_param_d)
response.json()

Dans le dossier dashboard, on trouve le code du dashboard qui s'appuie notament sur des outputs qui ne sont pas sur Github (problème de mémoire), mais qui sont générés par notre notebook P7_02_Modele.
Les fichiers Procfile et requirements sont utilisés par Heroku et sont indispensables pour le déploiement. (https://dashboardocp7.herokuapp.com/) 
Les ID (SK_ID_CURR) demandés dans le dashboard sont disponibles dans le fichier application test (téléchargeable sur Kaggle). 
Exemple d'ID : 100001 100005 100013 100028 100038 100042 100057 100065 100066 100067

Déploiement sur Heroku :
Créer un compte sur Heroku
Installer HEROKU CLI
Créer une nouvelle appli dans Heroku
se placer dans le dossier
git init 
git add app.py Procfile requirements.txt ...
git commit -m "first commit"
heroku login -i
heroku git:remote -a {your-project-name} #lier votre dossier local à appli Heroku
git push heroku master # push your code to heroku

