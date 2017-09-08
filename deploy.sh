#!/bin/sh

ROBOT_IP=10.0.0.17
IMACQ_IP=10.0.0.77
VISION_IP=10.0.0.117

ROBOT_USER=pi
IMACQ_USER=pi
VISION_USER=alex

rsync -avz ../EPypes/ --delete $ROBOT_USER@$ROBOT_IP:/home/$ROBOT_USER/code/EPypes/

rsync -avz ../EPypes/ --delete $IMACQ_USER@$IMACQ_IP:/home/$IMACQ_USER/code/EPypes/

rsync -avz ../EPypes/ --delete $VISION_USER@$VISION_IP:/home/$VISION_USER/code/EPypes/
