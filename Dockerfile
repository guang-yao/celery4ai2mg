FROM ai-image.imgo.tv/serving/ai2imgo_mxz:v2
ARG ci_name
ARG ci_token
RUN  cd /root/ && rm -rf celery_ai2mg && git config --global http.sslVerify false  && git config --global user.email "zhuyan@mgtv.com" && git config --global user.name "Jovian" && git clone  -b master  --depth=1 https://${ci_name}:${ci_token}@git.imgo.tv/aiops/celery_ai2mg.git
RUN  cd /root/celery_ai2mg  && pip install -r requirements.txt 
#RUN  cd /root/ai2mangguo  && git clone  -b master  --depth=1 https://${ci_name}:${ci_token}@git.imgo.tv/aiops/celery_ai2mg.git && python -m pip install -r requirements.txt  -i https://pypi.douban.com/simple/  && git clone -b master --depth=1 https://${ci_name}:${ci_token}@git.imgo.tv/aiops/multimedia_tools.git && cd multimedia_tools/ability && git clone -b master --depth=1 https://${ci_name}:${ci_token}@git.imgo.tv/aiops/common_data_type.git
#RUN  cd /root/ai2mangguo/spc_tools && git clone -b master --depth=1 https://${ci_name}:${ci_token}@git.imgo.tv/aiops/mangxiaozhi.git  && git clone -b master --depth=1 https://${ci_name}:${ci_token}@git.imgo.tv/aiops/qm-service.git qm_service
