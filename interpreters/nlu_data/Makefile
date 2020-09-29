rasa-train-default-nlu:
	rasa train nlu -c nlu_config.yml --nlu default/ --fixed-model-name default --verbose
tar-default-nlu:
	tar -xzvf models/default.tar.gz -C models/default/
train-default-nlu:
	make rasa-train-default-nlu tar-default-nlu

rasa-train-menu_or_help-nlu:
	rasa train nlu -c nlu_config.yml --nlu menu_or_help/ --fixed-model-name menu_or_help --verbose
tar-menu_or_help-nlu:
	tar -xzvf models/menu_or_help.tar.gz -C models/menu_or_help/
train-menu_or_help-nlu:
	make rasa-train-menu_or_help-nlu tar-menu_or_help-nlu

rasa-train-list_options-nlu:
	rasa train nlu -c nlu_config.yml --nlu list_options/ --fixed-model-name list_options --verbose
tar-list_options-nlu:
	tar -xzvf models/list_options.tar.gz -C models/list_options/
train-list_options-nlu:
	make rasa-train-list_options-nlu tar-list_options-nlu

train-all:
	make train-default-nlu train-menu_or_help-nlu train-list_options-nlu
