from keras.layers import Input, Dense
from keras.models import Model
from keras.datasets import mnist
from keras.utils import np_utils
from keras import regularizers
import numpy
from timeit import default_timer as timer
from keras import metrics
import numpy as np
from sklearn.metrics import classification_report
from sklearn.metrics import confusion_matrix
# Test case: 100 om values input
#number of clasess = 5
# sparsity constrain

input_number = 100
nb_classes = 10
#nb_epoch = 1000
batch_size = 100
#hidden_layer1 = 60
#hidden_layer2 = 40
#hidden_layer3 = 5 # because you have 10 categories
test_name = "100input_"
#(x_train, y_train), (x_test, y_test) = mnist.load_data()
#print(x_train[0])
#x_train = x_train.astype('float32') / 255.
#x_test = x_test.astype('float32') / 255.
#x_train = x_train.reshape((len(x_train), np.prod(x_train.shape[1:])))
#print(y_train)
#x_test = x_test.reshape((len(x_test), np.prod(x_test.shape[1:])))

# loading features dataset
dataset = numpy.loadtxt("om_featuresDB2.dat", delimiter=" ",usecols=range(1,102))
print("Dataset loaded")

numpy.random.shuffle(dataset)
#split into input (x) and output y variables
#print(sdf)
X = dataset[:,0:input_number].astype('float32')
Y = dataset[:,input_number].astype('float32')

#X = (X-X.min(0))/X.ptp(0)

x_train = X[:1200,]
x_test = X[1200:,]
y_train = Y[:1200,]
y_test = Y[1200:,]

# normalize train and test
minimun = x_train.min(0)
diff = x_train.ptp(0)
x_train = (x_train - minimun)/diff
x_test = (x_test - minimun)/diff

print('Train samples: {}'.format(x_train.shape[0]))
print('Test samples: {}'.format(x_test.shape[0]))

# categorize train and test output
y_train = np_utils.to_categorical(y_train, nb_classes)
y_test = np_utils.to_categorical(y_test, nb_classes)

#print(x_test[0])
#print(ad)

# 2*2*3*2 = 24 modelos de 100 entradas
l_epochs = [190]
l_fst_layer = [90, 80, 70]
l_snd_layer = [60, 50]

output = open(test_name + "training_network.dat","w+")
act = "softmax"
output.write("layer1 layer2 layer3 before_ft_accuracy after_ft_accuracy time\n")
for e in l_epochs:
  output.write("batch_size: " + str(e)+ "\n")
  for f in l_fst_layer:
    output.write("layers: " + str(f)+ " ")
    for s in l_snd_layer:
        print("training model: ")
        print(e,f,s,"\n")
        output.write(str(s) + " ")
        # begin training networks
        input_img = Input(shape=(input_number,))
        encoded = Dense(f, activation=act, activity_regularizer=regularizers.l1(10e-5))(input_img)
        encoded = Dense(s, activation=act, activity_regularizer=regularizers.l1(10e-5))(encoded)
        encoded = Dense(nb_classes, activation='softmax')(encoded)
        
        decoded = Dense(s, activation=act)(encoded)
        decoded = Dense(f, activation=act)(decoded)
        decoded = Dense(input_number, activation='softmax')(decoded)

        model = Model(input=input_img, output=encoded)
        model.compile(optimizer='rmsprop',
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        start = timer()
        model.fit(x_train, y_train,
                  nb_epoch=e,
                  batch_size=batch_size,
                  shuffle=True,
                  validation_data=(x_test, y_test),verbose=0)
        end = timer()
        elapsed  = end - start
        score = model.evaluate(x_test, y_test, verbose=1)
        
        output.write(str(score[0]) + " " + str(score[1]) + " " + str(elapsed))
        
        print('/n')
        print('Test score before fine tuning:', score[0] * 100)
        print('Test accuracy after fine tuning:', score[1] * 100)
        filename = "models/input100/" +str(e)+ "_" + str(f) +"_"+  str(s)+"_" 
       # serialize model to JSON
        model_json = model.to_json()
        with open(filename + "model.json", "w") as json_file:
            json_file.write(model_json)
        # serialize weights to HDF5
        model.save_weights(filename + "model.h5")
        print("Saved" + filename +" model to disk")
y_pred = model.predict(x_test)        
print("Testing done!")
matrix=confusion_matrix(y_test.argmax(axis=1), y_pred.argmax(axis=1))
print(matrix)



