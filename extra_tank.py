# solution
import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint


from opcua import Client
import time



# animate plots?
animate=True # True / False

# define tank model
def tank(Level,time,c,valve_position):

    rho = 1000.0 # water density (kg/m^3)
    A = 1.0      # tank area (m^2)

    # calculate derivative of the Level
    dLevel_dt = (c/(rho*A)) * valve_position

    return dLevel_dt

# --- OPC client --- :
url ="opc.tcp://localhost:4845"

client = Client(url)
client.connect()

'''
    Level : Initial level
    valve_position : Initial valve_position position (%)
'''
Level = client.get_node("ns=2;i=2").get_value()
valve_position = client.get_node("ns=2;i=3").get_value()
ubias = client.get_node("ns=2;i=4").get_value()
Kc = client.get_node("ns=2;i=5").get_value()
SP = client.get_node("ns=2;i=6").get_value()


print("OPC UA Client connected")

n_points = 1000

## --- Model Parameters --- :

# valve_position operation
c = 50.0          # valve_position coefficient (kg/s / %open)
u = np.zeros(n_points + 1) # u = valve_position % open


## --- Model Settings --- 

# time span for the simulation for 10 sec, every 0.1 sec
ts = np.linspace(0,10,n_points + 1)

# for storing the results
z = np.zeros(n_points + 1)
es = np.zeros(n_points + 1)
sps = np.zeros(n_points + 1)

# TO DO: what is the value for ubias?
# ubias = 0

# TO DO: decide on a tuning value for Kc
# Kc = 75.0

# TO DO: record the desired level (set point)
# SP = 10

while True:
        
    # plt.figure(1,figsize=(12,5))
    # if animate:
    #     plt.ion()
    #     plt.show()
    #     make_gif = True
    #     try:
    #         import imageio  # required to make gif animation
    #     except:
    #         print('install imageio with "pip install imageio" to make gif')
    #         make_gif=False
    #     if make_gif:
    #         try:
    #             import os
    #             images = []
    #             os.mkdir('./frames')
    #         except:
    #             print('Figure directory failed')
    #             make_gif=False

    # simulate with ODEINT
    for i in range(n_points):
    
        # 
        # Level = client.get_node("ns=2;i=2").get_value()
        #valve_position = client.get_node("ns=2;i=3").get_value()
        ubias = client.get_node("ns=2;i=4").get_value()
        Kc = client.get_node("ns=2;i=5").get_value()
        SP = client.get_node("ns=2;i=6").get_value()


        # calculate the error
        error = SP - Level

        # TO DO: put P-only controller here
        valve_position = ubias + Kc * error
        valve_position = max(0,valve_position)
        valve_position = min(100,valve_position)
        
        

        u[i+1] = valve_position   # b
        es[i+1] = error  # store the error 

        y = odeint(tank,Level,[0,0.1],args=(c,valve_position))

        # Seding data to OPC 
        
        Level = y[-1] # take the last point
        z[i+1] = Level # store the level for plotting
        sps[i+1] = SP
          
        print(i)
        print(valve_position)

        try:
            client.get_node("ns=2;i=2").set_value(Level[0])
            client.get_node("ns=2;i=3").set_value(valve_position)
        except:
            client.get_node("ns=2;i=3").set_value(valve_position[0])

        #ubias = client.get_node("ns=2;i=4").set_value()
        #Kc = client.get_node("ns=2;i=5").set_value()
        #SP = client.get_node("ns=2;i=6").set_value()    


        if animate:
            # update plot
            plt.clf()

            plt.subplot(3,1,1)
            plt.plot(ts[0:i+1],z[0:i+1],'r-',linewidth=3,label='level PV')
            plt.plot(ts[0:i+1],sps[0:i+1],'k:',linewidth=3,label='level SP')
            plt.ylabel('Tank Level')
            plt.legend(loc='best')
            
            plt.subplot(3,1,2)
            plt.plot(ts[0:i+1],u[0:i+1],'b--',linewidth=3,label='valve_position')
            plt.ylabel('Valve_position')    
            plt.legend(loc='best')

            plt.subplot(3,1,3)
            plt.plot(ts[0:i+1],es[0:i+1],'g-',linewidth=3,label='error')
            plt.ylabel('Error = SP-PV')
            plt.xlabel('Time (sec)')
            plt.legend(loc='best')

            # filename='./frames/frame_'+str(1000+i)+'.png'
            # plt.savefig(filename)

            # if make_gif:
            #     images.append(imageio.imread(filename))
            plt.pause(0.8)

    # if not animate:
    #     # plot results
    #     plt.subplot(3,1,1)
    #     plt.plot(ts,z,'r-',linewidth=3,label='level PV')
    #     plt.plot(ts,sps,'k:',linewidth=3,label='level SP')
    #     plt.ylabel('Tank Level')
    #     plt.legend(loc='best')
    #     plt.subplot(3,1,2)
    #     plt.plot(ts,u,'b--',linewidth=3,label='valve_position')
    #     plt.ylabel('Valve_position')    
    #     plt.legend(loc='best')
    #     plt.subplot(3,1,3)
    #     plt.plot(ts,es,'g-',linewidth=3,label='error')
    #     plt.ylabel('Error = SP-PV')    
    #     plt.xlabel('Time (sec)')
    #     plt.legend(loc='best')
    #     plt.show()
    # # else:
    #     # # create animated GIF
    #     # if make_gif:
    #     #     imageio.mimsave('animate.gif', images)