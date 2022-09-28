FROM mongo
WORKDIR /_init
COPY mongo-init.sh .
RUN chmod +x mongo-init.sh
CMD [ "bash", "-c", "/_init/mongo-init.sh"]