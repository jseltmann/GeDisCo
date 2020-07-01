INPPATH="/home/users/jseltmann/data/europarl/europarl-v7.cs-en.20k.processed.cs"
REFERENCE="/home/users/jseltmann/data/europarl/europarl-v7.cs-en.20k.processed.en"
#INPPATH="/home/users/jseltmann/data/europarl/fr-en/europarl-v7.fr-en.20k.processed.fr"
#REFERENCE="/home/users/jseltmann/data/europarl/fr-en/europarl-v7.fr-en.20k.processed.en"
WORKDIR="/home/users/jseltmann/project/tools/moses/cz_tuning/"
EXEPATH=~/project/tools/moses/ubuntu-16.04/bin/moses
INIPATH="/home/users/jseltmann/project/tools/cz_models/moses.ini.1"

./mert-moses.pl $INPPATH $REFERENCE $EXEPATH $INIPATH \
	--working-dir $WORKDIR \
	--cache-model $WORKDIR \
