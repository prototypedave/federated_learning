import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


if __name__ == "__main__":
    # Sample data
    x = [1, 2, 3, 4, 5]
    y = [5, 6, 7, 8, 9]
    z = [10, 11, 12, 13, 14]

    # Create a 3D axis
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Create 3D scatter plot
    ax.bar(x, y, z)

    # Set labels for each axis
    ax.set_xlabel('X Label')
    ax.set_ylabel('Y Label')
    ax.set_zlabel('Z Label')

    # Show the plot
    plt.show()
