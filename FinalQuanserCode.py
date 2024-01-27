#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import random
        
def randomize_spawn(cages):
    if not cages:
        return cages, ["", ""]

    cage_num = random.choice(cages)
    cages.remove(cage_num)
    arm.spawn_cage(cage_num)

    cage_id_map = {
        1: ["red", "small"],
        2: ["green", "small"],
        3: ["blue", "small"],
        4: ["red", "large"],
        5: ["green", "large"],
        6: ["blue", "large"],
    }

    cage_id = cage_id_map.get(cage_num, ["", ""])
    
    return cages, cage_id

def pick_up(position):

    #move arm to cage spawn position
    arm.move_arm(position[0],position[1],position[2])
    time.sleep(0.5)

    #close gripper
    arm.control_gripper(45)
    time.sleep(0.5)

    #arm moves to home position
    arm.home()
    time.sleep(0.5)
    
def rotate_arm_base():
    x = 0
    position_o = 0
    
    while x != 1:
        position = (potentiometer.right()*100-50)*170/50
        
        if position != position_o:
            arm.rotate_base(position-position_o)
        
        position_o = position
    
def drop_off(container_id):
    
    container_colour = container_id[0]
    container_size = container_id[1]
    arm.activate_autoclaves()

    #set control variable as false
    container_dropped_off = False
    
    while container_dropped_off:
        
        pLeft = potentiometer.left()
        
        #if left potentiometer value is > 0.5 and < 1.0 and the container size is small
        if ((pLeft < 1.0) and (pLeft > 0.5)) and (container_size == "small"):
            
            #bring container to the top of the autoclave
            arm.rotate_elbow(-15)
            time.sleep(0.5)
            
            arm.rotate_shoulder(35)
            time.sleep(0.5)
            
            #drop container inside autoclave
            arm.control_gripper(-45)
            time.sleep(0.5)
           
            #return arm home
            arm.home()
            time.sleep(0.5)
            
            dropped_off = True
        
        #if left potentiometer value is 1.0 and the container size is large
        elif (pLeft == 1.0) and (container_size == "large"):
            
            #open the specfic coloured autoclave 
            arm.open_autoclave(container_colour)
            time.sleep(0.5)
            
            arm.rotate_elbow(30)
            time.sleep(0.5)
            
            arm.rotate_shoulder(20)
            time.sleep(0.5)
            
            arm.control_gripper(-45)
            time.sleep(0.5)
            
            arm.home()
            time.sleep(0.5)
            
            #close the specfic coloured autoclave
            arm.open_autoclave(container_colour, False)
            time.sleep(0.5)
            
            dropped_off = True
    
    arm.deactivate_autoclaves()
    
def main():

    #cage characteristics placeholder for colour in first index and size in second index
    cage_id = ["",""]
    cage_nums = [1,2,3,4,5,6]
    
    #position of cage spawn
    cage_spawn_position = [-0.064,0.566,0.026]
    
    while (len(cage_nums) > 0):  
        #Spawns in random cage and removes it from the cages able to spawn
        cage_nums, cage_id = randomize_spawn(cage_nums)
        
        #Picks up the object
        pick_up(cage_spawn_position)
        rotate_arm_base()
        drop_off(cage_id)
        
main()

