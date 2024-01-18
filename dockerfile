# Utilisez l'image de base Python
FROM python:3.8

# Définissez le répertoire de travail dans le conteneur
WORKDIR /app

# Copiez le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installez les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copiez le reste des fichiers de l'application dans le conteneur
COPY src .

# Commande à exécuter lors du démarrage du conteneur
CMD ["python", "__main__.py"]