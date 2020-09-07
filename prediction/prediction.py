from tensorflow.keras.models import load_model


def getPrediction(client, input_test, output_test):

    model = load_model('models/model-'+client+'.h5')

    test_loss, test_acc = model.evaluate(input_test, output_test, verbose=2)

    print('\nTest accuracy:', test_acc)

    predictions = model.predict(input_test)

#    for i in range (0, output_test.shape[0]):
#        for j in range (0, output_test.shape[1]):
#            predictions[i][j] = math.floor(predictions[i][j] + 0.5)
#        print(output_test[i], predictions[i])

    return predictions
