FROM python:2.7.11-onbuild
MAINTAINER Michael Hausenblas "michael.hausenblas@gmail.com"
ENV REFRESHED_AT 2016-01-02T18:05
EXPOSE 9876
CMD [ "python", "./kploy-app-registry.py" ]