import numpy as np
import matplotlib.pyplot as plt

fc = 5e9
wavelength = 3e8 / fc
d = 0.5 * wavelength # in meters

# generalized steering vector equation, given element positions and a direction vector (which is a 3x1 unit vector of x,y,z)
def steering_vector(pos, dir):
    #                           Nrx3  3x1   
    return np.exp(-2j * np.pi * pos @ dir / wavelength) # Nrx1 (column vector)

# Let's start with 1D, using a 4-element ULA
Nr = 4

# We will store our element positions in a list of (x,y,z)'s, even though it's just a ULA along the y-axis
pos = np.zeros((Nr, 3)) # Element positions, as a list of x,y,z coordinates in meters
for i in range(Nr):
    pos[i,0] = 0     # x position
    pos[i,1] = d * i # y position
    pos[i,2] = 0     # z position

# Plot positions of elements, top-down view, so no z-axis shown
if False:
    plt.plot(pos[:,0], pos[:,1], 'o')
    plt.xlim([-0.05, 0.05])
    plt.ylim([-0.01, 0.1])
    plt.xlabel("X Position [m]")
    plt.ylabel("Y Position [m]")
    plt.grid()
    plt.gca().set_aspect('equal', adjustable='box')
    # Draw an arrow to show theta
    theta = np.deg2rad(20) # point towards 20 degrees
    plt.arrow(0, float(np.mean(pos[:,1])), np.sin(theta)*0.03, np.cos(theta)*0.03, head_width=0.005, head_length=0.005, fc='r', ec='r')
    plt.text(0.018, 0.07, 'theta (20 deg)', color='red')
    plt.savefig('../_images/2d_beamforming_ula.svg', bbox_inches='tight')
    plt.show()
    exit()

# With 1D, we only care about one angle, theta, which we will consider the azmiuth
theta = np.deg2rad(60) # azimith angle. point towards 60 degrees as an example

# The direction unit vector pointing towards theta is:
dir = np.asmatrix([np.sin(theta), # x component
                   np.cos(theta), # y component 
                   0]             # z component
                   ).T
print("dir:\n", dir) # Remember that it's a unit vector representing a direction, it's not in meters

# Now let's use our generalized steering vector function to calculate the steering vector
s = steering_vector(pos, dir)

# Use the conventional beamformer, which is simply the weights equal to the steering vector, plot the beam pattern
w = s
print("weights:\n", w)

# Visualize beam pattern when using these weights
if False:
    # This code is for plotting the beam pattern, it essentially emulates a signal coming in from different angles, then applies the weights to it
    theta_scan = np.linspace(0, 2*np.pi, 1000) # 1000 different thetas for nice resolution
    results = []
    for theta_i in theta_scan:
        dir_theta_i = np.asmatrix([np.sin(theta_i), np.cos(theta_i), 0]).T
        a = steering_vector(pos, dir_theta_i) # array factor
        resp = w.conj().T @ a # scalar
        results.append(10*np.log10(np.abs(resp)[0,0])) # power in signal, in dB
    fig, ax = plt.subplots(subplot_kw={'projection': 'polar'})
    ax.plot(theta_scan, results)
    ax.plot([theta, theta], [-30, 10], 'r--')
    #ax.set_rlabel_position(55) # type: ignore # Move grid labels away from other labels
    ax.set_ylim((-30, 10)) # because there's no noise, only go down 30 dB
    plt.show()
    exit()

# Now let's switch to 2D, using a 4x4 array with half wavelength spacing, so 16 elements total
Nr = 16

# Element positions, still as a list of x,y,z coordinates in meters, we'll place the array in the X-Z plane
pos = np.zeros((Nr,3))
for i in range(Nr):
    pos[i,0] = d * (i % 4)  # x position
    pos[i,1] = 0            # y position
    pos[i,2] = d * (i // 4) # z position

# Plot positions of elements
if False:
    plt.plot(pos[:,0], pos[:,2], 'o')
    plt.xlim([-0.01, 0.1])
    plt.ylim([-0.01, 0.1])
    plt.xlabel("X Position [m]")
    plt.ylabel("Z Position [m]")
    plt.grid()
    plt.gca().set_aspect('equal', adjustable='box')
    plt.savefig('../_images/2d_beamforming_element_pos.svg', bbox_inches='tight')
    plt.show()
    exit()

# We will introduce phi, the elevation angle. Let's point towards an arbitrary direction
theta = np.deg2rad(60) # azimith angle
phi = np.deg2rad(30) # elevation angle

# Using our spherical coordinate convention, we can calculate the unit vector:
def get_unit_vector(theta, phi):  # angles are in radians
    return np.asmatrix([np.sin(theta) * np.cos(phi), # x component
                        np.cos(theta) * np.cos(phi), # y component
                        np.sin(phi)]).T              # z component

dir = get_unit_vector(theta, phi)
print("dir:\n", dir) # Remember that it's a unit vector representing a direction, it's not in meters

# Now let's use our generalized steering vector function to calculate the steering vector
s = steering_vector(pos, dir)

# Use the conventional beamformer, which is simply the weights equal to the steering vector, plot the beam pattern
w = s
print("weights:\n", w)

# At this point it's worth pointing out that we didn't actually change dimensionality of anything, going from 1D to 2D, we just have a non-zero y component, the steering vector equation is still the same and the weights are still a 1D array
# Some folks might assemble their weights as a 2D array so that visually it matches the array geometry, but it's not necessary and best to keep it 1D

# 2D contour plot from Tarun
if False:
    AZ_MIN = -180
    AZ_MAX = 180
    AZ_RES = 1
    EL_MIN = 0
    EL_MAX = 180
    EL_RES = 1

    az_range_rad = np.radians( np.arange(AZ_MIN, AZ_MAX, AZ_RES))[None,:] #1x360
    el_range_rad = np.radians( np.arange(EL_MIN, EL_MAX, EL_RES))[:,None] #180x1
    k = 2 * np.pi * np.asarray([fc]*Nr) / 3e8                                   #3x0,
    kx = k[0] * np.sin(el_range_rad) * np.cos(az_range_rad)                  #180*360
    ky = k[0] * np.sin(el_range_rad) * np.sin(az_range_rad)                  #180*360
    kz = k[0] * np.cos(el_range_rad)   #180x1 
    # print(np.arange(az_min, az_max, az_res))                                     #180x1
    # print(az_range_rad.shape)
    # print(el_range_rad.shape)
    print('kx shape:', kx.shape)
    print('ky shape:', ky.shape)
    print('kz shape:', kz.shape)
    scan_kx = np.exp(-1j  * (kx[:,:,None] * np.arange(4) * d))[:,:,None,:] # 180x360x1x10
    scan_kz =  np.exp(-1j * (kz[:,:,None] * np.arange(4) * d))[:, :,:,None] # 180x360x10x1
    print('scan_kx shape:', scan_kx.shape)
    print('scan_kz shape:', scan_kz.shape)
    
    scan_overall = scan_kx*scan_kz
    print('scan_overall shape:', scan_overall.shape)

    scan_overall = scan_overall.reshape((scan_overall.shape[0], scan_overall.shape[1], -1)) #180x360x100
    # scan_overall = np.reshape(scan_overall, (180,360,100), order= 'C') #180x360x100

    print('scan_overall shape:', scan_overall.shape) # (180, 360, 16)

    weight_conj_t = w.conj().T 
    # add another dimension to the weight vector to make it 1x1x16
    weight_conj_t = np.expand_dims(weight_conj_t, axis=0) # 1x1x16
    print('weight vector shape:',weight_conj_t.shape) # (1, 16)

    results = np.sum(weight_conj_t * scan_overall, axis=2) #180x360
    results = np.abs(results)
    #results = results**2
    #results = 10 * np.log10(results) # Convert to dB

    plt.figure(figsize=(8, 6))
    im = plt.imshow(results, 
                    extent=(AZ_MIN, AZ_MAX, EL_MIN, EL_MAX),
                    cmap='viridis', 
                    origin='lower')
                    #vmax=15,
                    #vmin=-30,
                    #aspect='auto')
    plt.colorbar(im)
    plt.xlabel('Azimuth Angle (degrees)')
    plt.ylabel('Elevation Angle (degrees)')
    plt.grid()
    plt.show()


# 2D plot that makes more sense
# This seems to be making a UV plot
if False:
    resolution = 100 # number of points in each direction
    theta_scan = np.linspace(-np.pi/2, np.pi/2, resolution) # azimuth angles
    phi_scan = np.linspace(-np.pi/4, np.pi/4, resolution) # elevation angles
    results = np.zeros((resolution, resolution)) # 2D array to store results
    for i, theta_i in enumerate(theta_scan):
        for j, phi_i in enumerate(phi_scan):
            a = steering_vector(pos, get_unit_vector(theta_i, phi_i)) # array factor
            results[i, j] = np.abs(w.conj().T @ a)[0,0] # power in signal, in dB
    plt.imshow(results, extent=(theta_scan[0]*180/np.pi, theta_scan[-1]*180/np.pi, phi_scan[0]*180/np.pi, phi_scan[-1]*180/np.pi), origin='lower', aspect='auto', cmap='viridis')
    plt.colorbar(label='Power [dB]')
    plt.scatter(theta*180/np.pi, phi*180/np.pi, color='red', s=50) # Add a dot at the correct theta/phi
    plt.xlabel('Azimuth angle [degrees]')
    plt.ylabel('Elevation angle [degrees]')
    plt.savefig('../_images/2d_beamforming_2dplot.svg', bbox_inches='tight')
    plt.show()
    exit()


# Visualize beam pattern when using these weights, but this time we need a 3D surface plot
# Note that this is not a polar plot, it's using X and Y to represent the azimuth and elevation angles, and Z to represent the power in dB
if False:
    resolution = 100 # number of points in each direction
    theta_scan = np.linspace(-np.pi/2, np.pi/2, resolution) # azimuth angles
    phi_scan = np.linspace(-np.pi/4, np.pi/4, resolution) # elevation angles
    results = np.zeros((resolution, resolution)) # 2D array to store results
    for i, theta_i in enumerate(theta_scan):
        for j, phi_i in enumerate(phi_scan):
            dir_i = get_unit_vector(theta_i, phi_i)
            a = steering_vector(pos, dir_i) # array factor
            resp = w.conj().T @ a # scalar
            results[i, j] = 10*np.log10(np.abs(resp)[0,0]) # power in signal, in dB
    # plot_surface needs x,y,z form
    results = 10*np.log10(results) # convert to dB
    #results[results < -10] = -10 # crop the z axis to some level of dB
    fig, ax = plt.subplots(subplot_kw={"projection": "3d", "computed_zorder": False})
    surf = ax.plot_surface(np.rad2deg(theta_scan[:,None]), # type: ignore
                                                    np.rad2deg(phi_scan[None,:]),
                                                    results,
                                                    cmap='viridis')
    #ax.set_zlim(-10, results[max_idx])
    ax.set_xlabel('Azimuth (theta)')
    ax.set_ylabel('Elevation (phi)')
    ax.set_zlabel('Power [dB]') # type: ignore
    fig.savefig('../_images/2d_beamforming_3dplot.svg', bbox_inches='tight')
    plt.show()
    exit()


# Let's simulate some actual samples now, we'll add two tone jammers coming it from different directions. Same 4x4 array, same element positions (pos variable)
N = 10000 # number of samples to simulate

jammer1_theta = np.deg2rad(-30)
jammer1_phi = np.deg2rad(10)
jammer1_dir = get_unit_vector(jammer1_theta, jammer1_phi)
jammer1_s = steering_vector(pos, jammer1_dir) # Nr x 1
jammer1_tone = np.exp(2j*np.pi*0.1*np.arange(N)).reshape(1,-1) # make a row vector

jammer2_theta = np.deg2rad(10)
jammer2_phi = np.deg2rad(50)
jammer2_dir = get_unit_vector(jammer2_theta, jammer2_phi)
jammer2_s = steering_vector(pos, jammer2_dir)
jammer2_tone = np.exp(2j*np.pi*0.2*np.arange(N)).reshape(1,-1) # make a row vector

noise = np.random.normal(0, 1, (Nr, N)) + 1j * np.random.normal(0, 1, (Nr, N)) # complex Gaussian noise
r = jammer1_s @ jammer1_tone + jammer2_s @ jammer2_tone + noise # produces 16 x 10000 matrix of samples

# Calc the MVDR beamformer weights towards theta/phi direction we were using earlier (unit vector in that direction is still saved as dir)
s = steering_vector(pos, dir) # 16 x 1
R = np.cov(r) # Covariance matrix, 16 x 16
Rinv = np.linalg.pinv(R)
w = (Rinv @ s)/(s.conj().T @ Rinv @ s) # MVDR/Capon equation
print("weights:\n", w)

# Look at beam pattern towards misc directions

# Power in the direction we are pointing (theta=60, phi=30, which is still saved as dir):
a = steering_vector(pos, dir) # array factor
resp = w.conj().T @ a # scalar
print("Power in direction we are pointing:", 10*np.log10(np.abs(resp)[0,0]), 'dB')

# Power in the direction of jammer 1:
a = steering_vector(pos, jammer1_dir) # array factor
resp = w.conj().T @ a # scalar
print("Power in direction of jammer 1:", 10*np.log10(np.abs(resp)[0,0]), 'dB')

# Power in the direction of jammer 2:
a = steering_vector(pos, jammer2_dir) # array factor
resp = w.conj().T @ a # scalar
print("Power in direction of jammer 2:", 10*np.log10(np.abs(resp)[0,0]), 'dB')

# Power in the direction slightly off (1 deg in each axis) from where we are pointing:
theta_off = np.deg2rad(61) # azimith angle
phi_off = np.deg2rad(31) # elevation angle
dir_off = get_unit_vector(theta_off, phi_off)
a = steering_vector(pos, dir_off) # array factor
resp = w.conj().T @ a # scalar
print("Power in direction slightly off from where we are pointing:", 10*np.log10(np.abs(resp)[0,0]), 'dB')

# Power towards a random direction:
theta_rand = np.deg2rad(360 * np.random.rand()) # azimith angle
phi_rand = np.deg2rad(90 * np.random.rand()) # elevation angle
dir_rand = get_unit_vector(theta_rand, phi_rand)
a = steering_vector(pos, dir_rand) # array factor
resp = w.conj().T @ a # scalar
print("Power in a random direction:", 10*np.log10(np.abs(resp)[0,0]), 'dB')

# MVDR keeps the power in the direction we point to 0 dB, and makes nulls in the directions of other signals (like our jammers)
# So we end up getting a pretty low value towards the jammers
# Slightly off from where we are pointing, we get a value a tad below 0 dB
# Towards a random direction, we get a value higher than the jammers but way lower than 0 dB, most of the time

# Sanity check the max gain from MVDR
resolution = 200 # number of points in each direction
theta_scan = np.linspace(0, 2*np.pi, resolution) # azimuth angles
phi_scan = np.linspace(0, np.pi, resolution) # elevation angles
results = np.zeros((resolution, resolution)) # 2D array to store results
for i, theta_i in enumerate(theta_scan):
    for j, phi_i in enumerate(phi_scan):
        dir_i = get_unit_vector(theta_i, phi_i)
        a = steering_vector(pos, dir_i) # array factor
        resp = w.conj().T @ a # scalar
        results[i, j] = 10*np.log10(np.abs(resp)[0,0]) # power in signal, in dB
print(np.max(results)) # about 0 dB
# Print argmax of a 2d array
max_idx = np.unravel_index(np.argmax(results, axis=None), results.shape)
print(theta_scan[max_idx[0]] * 180 / np.pi) # theta doesnt really mean anything here because phi is close to 0
print(phi_scan[max_idx[1]] * 180 / np.pi) # phi is sometimes +10 and sometimes -10 deg
