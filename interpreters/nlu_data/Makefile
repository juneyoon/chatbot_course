rasa-train-default-nlu:
	rasa train nlu -c nlu_config.yml --nlu default/ --fixed-model-name default --verbose
tar-default-nlu:
	tar -xzvf models/default.tar.gz -C models/default/
train-default-nlu:
	make rasa-train-default-nlu tar-default-nlu
