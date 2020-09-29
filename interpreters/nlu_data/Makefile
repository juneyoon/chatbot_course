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

rasa-train-order-nlu:
	rasa train nlu -c nlu_config.yml --nlu order/ --fixed-model-name order --verbose
tar-order-nlu:
	tar -xzvf models/order.tar.gz -C models/order/
train-order-nlu:
	make rasa-train-order-nlu tar-order-nlu

rasa-train-final_order-nlu:
	rasa train nlu -c nlu_config.yml --nlu final_order/ --fixed-model-name final_order --verbose
tar-final_order-nlu:
	tar -xzvf models/final_order.tar.gz -C models/final_order/
train-final_order-nlu:
	make rasa-train-final_order-nlu tar-final_order-nlu

train-all:
	make train-default-nlu train-menu_or_help-nlu train-list_options-nlu train-order-nlu train-final_order-nlu
