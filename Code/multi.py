import multiprocessing

def run_depth_estimation():
    # code for depth estimation

def run_object_detection():
    # code for object detection

def run_navigation_guidance():
    # code for navigation guidance

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=run_depth_estimation)
    p2 = multiprocessing.Process(target=run_object_detection)
    p3 = multiprocessing.Process(target=run_navigation_guidance)

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
