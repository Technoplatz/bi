FROM mongo
RUN rm -rf /_replicaset
RUN mkdir /_replicaset
WORKDIR /_replicaset
COPY mongo-replicaset.sh .
COPY sample-data/ ./sample-data/
RUN chmod +x /_replicaset/mongo-replicaset.sh
CMD [ "bash", "-c", "/_replicaset/mongo-replicaset.sh"]