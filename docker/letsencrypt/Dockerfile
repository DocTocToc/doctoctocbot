FROM certbot/certbot                                                            
MAINTAINER jerome <jerome4@jerome.cc>                                           
                                                                                
RUN apk add docker bash grep coreutils                                                          
                                                                                
ADD start.sh /bin/start.sh                                                      
                                                                                
ENTRYPOINT [ "/bin/start.sh" ]