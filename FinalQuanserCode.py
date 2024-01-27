ip_address = 'localhost' # Enter your IP Address here
#--------------------------------------------------------------------------------
import sys
sys.path.append('../')
from Common.simulation_project_library import *

hardware = False
QLabs = configure_environment(project_identifier, ip_address, hardware).QLabs
arm = qarm(project_identifier,ip_address,QLabs,hardware)
potentiometer = potentiometer_interface()
#---------------------------------------------------------------------------------

import random


#function selects a random cage from the available cages, removes it from the list of cages, and spawns in the selected cage  
def randomize_spawn(cages):

   #select a random cage number from the available spawnable cages
   cage_num = random.choice(cages)
   #remove selected cage from the list of cages that can spawn, ensuring that the same cage is not spawned again
   cages.remove(cage_num)
   #spawn the selected cage
   arm.spawn_cage(cage_num)

   #map the cage number to its characteristics (color and size) using a predefined dictionary
   cage_id_map = {
       1: ["red", "small"],
       2: ["green", "small"],
       3: ["blue", "small"],
       4: ["red", "large"],
       5: ["green", "large"],
       6: ["blue", "large"],
   }
   
   #get the characteristics of the selected cage, defaulting to the placeholder list if not found
   cage_id = cage_id_map.get(cage_num, ["", ""])

   #update global variables cage_color and cage_size based on the selected cage. 
   global cage_color
   global cage_size
   #initialize cage_color to the first index position of the cage_id list
   cage_color = cage_id[0]
   #initialize cage_size to the second index position of the cage_id list
   cage_size = cage_id[1]

   #if the argument passing through the function (cages) is empty
   if not cages:
       #return cages and a placeholder list to avoid errors in the case where there are no more cages to spawn
       return cages, ["", ""]
                       
   #return updated list of cages and the characteristics of the spawned cage
   return cages, cage_id


#function pick ups cage with the arm from its spawn position
def pick_up(cage_spawn_position):

   #move arm to cage spawn position (the argument passed through the function)
   arm.move_arm(cage_spawn_position[0],cage_spawn_position[1],cage_spawn_position[2])
   #add delay for 2 seconds to allow the arm to reach the specified position
   time.sleep(2)

   #close gripper of the arm to grab the cage
   arm.control_gripper(45)
   #add delay for 2 seconds to allow the gripper to close securely around the cage
   time.sleep(2)

   #arm moves to home position after picking up the cage
   arm.move_arm(0.406, 0.0, 0.483)
   #add delay for 2 seconds to allow the arm to reach its home position
   time.sleep(2)


#function handles the rotation of the arm's base until it reaches the correct autoclave
def rotate_arm_base():
  
   #get initial reading from the right potentiometer
   old_reading = potentiometer.right()
  
   #allow user to rotate the arm's base until it's at the correct autoclave
   while arm.check_autoclave(cage_color) == False:
 
       #get the new reading from the right potentiometer and scale it
       new_reading = (potentiometer.right()*100-50)*170/50
     
       #if there's a change in the reading, rotate the arm's base accordingly
       if new_reading != old_reading:
           arm.rotate_base(new_reading-old_reading)

       #if there's no change in the reading, update the old reading for the next iteration in the while loop
       else:
           old_reading = new_reading
 

#function drops off the cage at its corresponding autoclave
def drop_off():

   #activate autoclaves
   arm.activate_autoclaves()
   #initialize control variable as false
   dropped_off = False 

   while dropped_off == False:
   
       #if left potentiometer value is > 0.5 and < 1.0 and the cage size is small
       if ((potentiometer.left() < 1.0) and (potentiometer.left() > 0.5)) and (cage_size == "small"):
          
           #add delay for 2 seconds
           time.sleep(2)

           #move arm to the position hovering over the specific colored autoclave based on the cage's color
           if cage_color == 'red':
               arm.move_arm(0.0,0.679,0.363)
           elif cage_color == 'blue':
               arm.move_arm(0.0,-0.679,0.363)
           else:
               #for green small-sized cage
               arm.move_arm(-0.618,0.225,0.363)

           #add delay for 2 seconds to allow the arm to reach the autoclave
           time.sleep(2)
     
           #open arm's gripper to release the cage
           arm.control_gripper(-20)
           #add delay for 2 seconds to ensure the cage is fully released
           time.sleep(2)

           #return arm to home position
           arm.home()
           #add delay for 2 seconds to allow the arm to reach its home position
           time.sleep(2)

           #set control variable as true to exit out of the while loop
           dropped_off = True
   
       #if left potentiometer value is 1.0 and the cage size is large
       elif (potentiometer.left() == 1.0) and (cage_size == "large"):
          
           #add delay for 2 seconds
           time.sleep(2)

           #open the specific colored autoclave
           arm.open_autoclave(cage_color)
           #add delay for 2 seconds to allow autoclave to be fully opened
           time.sleep(2)
       
           #move arm to the position hovering over the specific colored autoclave's drawer based on the cage's color
           if cage_color == 'red':
               arm.move_arm(0.0,0.428,0.194)
           elif cage_color == 'blue':
               arm.move_arm(0.0,-0.428,0.194)
           else:
               #for green large-sized cage
               arm.move_arm(-0.446,0.162,0.204)
           #add delay for 2 seconds to allow the arm to reach the autoclave
           time.sleep(2)
       
           #open arm's gripper to release the cage
           arm.control_gripper(-30)
           #add delay for 2 seconds to ensure the cage is fully released
           time.sleep(2)
       
           #return arm to home position
           arm.home()
           time.sleep(2)
       
           #close the specific coloured autoclave
           arm.open_autoclave(cage_color, False)
           #add delay for 2 seconds to allow the arm to reach its home position
           time.sleep(2)

           #set control variable as true to exit out of the while loop
           dropped_off = True

   #deactivate autoclaves
   arm.deactivate_autoclaves()


#main function utilizes all the functions in the program for spawning, picking up, rotating the arm base, and dropping off cages until all six cages have been processed
def main():

   #cage characteristics placeholder for color in first index and size in second index
   cage_id = ["",""]
   #initialize list with the numbers of available cages that can be spawned
   cage_nums = [1,2,3,4,5,6]
 
   #position of cage spawn
   cage_spawn_position = [0.617, 0.054, 0.044]
 
   #continue the loop until there are no more cages left to spawn
   while (len(cage_nums) > 0):
       
       #spawn in random cage and remove it from the list of cages able to spawn
       cage_nums, cage_id = randomize_spawn(cage_nums)
     
       #pick up the cage from the spawn position
       pick_up(cage_spawn_position)

       #rotate the arm base until it reaches correct autoclave
       rotate_arm_base()

       #drop off the cage into the autoclave
       drop_off()

main()