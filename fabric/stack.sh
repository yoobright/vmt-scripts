fab -f vmtdeploy.py deploy_cache
fab -f stack.py start_tgt && \
fab -f stack.py my_stack
