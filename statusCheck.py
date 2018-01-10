#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time       : 2018/1/9 16:10
# @Author     : 周星星 Siman Chou
# @Site       : https://github.com/simanchou
# @File       : statusCheck.py
# @Description: 
import socket
import docker
import yaml
import os
import requests
import time


def getConf(file="conf.yml"):
    conf_file = os.path.join(os.path.split(os.path.realpath(__file__))[0], file)
    if os.path.exists(conf_file):
        with open(conf_file, "r", encoding="utf-8") as fp:
            conf = yaml.load(fp.read())
        return conf
    else:
        print("Error,while loading conf file '{}'".format(file))
        return None


def getDockerStatus():
    conf = getConf()
    client = docker.DockerClient(base_url=conf['dockerAPI'])

    dockerStates = ["created", "restarting", "running", "removing", "paused", "exited", "dead"]
    containerStatusDict = {}
    for state in dockerStates:
        containerStatusDict[state] = []

    for container in client.containers.list(1):
        containerStatusDict[container.status].append(container.name)

    pushData = {}
    for k, v in containerStatusDict.items():
        pushData[k] = (len(v), [service for service in v])

    return pushData


def exportToGateway(gateway, job, group, instance, host, env):
    gwUrl = "http://{}/metrics/job/{}/group/{}/instance/{}/host/{}/env/{}".format(gateway,
                                                                                  job,
                                                                                  group,
                                                                                  instance,
                                                                                  host,
                                                                                  env)
    data = ""

    for k, v in getDockerStatus().items():
        if v[0]:
            for name in v[1]:
                data += "docker_status{} {}\n".format("{}status=\"{}\",containername=\"{}\"{}".format("{", k, name, "}"), 1)

    r = requests.put(gwUrl, data=data)
    print(data)
    return r.text



if __name__ == "__main__":
    #print(getDockerStatus())

    conf = getConf()

    gateway = conf["gateway"]
    job = conf["job"]
    group = conf["group"]
    env = conf["env"]

    hostName = socket.gethostname()
    if "." in hostName:
        instance = host = hostName.split(".")[0]
    else:
        instance = host = hostName

    if conf["interval"]:
        interval = conf["interval"]
    else:
        interval = 60

    while True:
        exportToGateway(gateway, job, group, instance, host, env)
        print("Push to gateway successful at {}".format(time.asctime()))
        time.sleep(interval)
