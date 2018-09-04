import matlab.engine
eng = matlab.engine.start_matlab()
content = eng.load("AllTariffs.mat",nargout=1)
x = 1