import tensorflow as tf
from tensorflow import keras
from commonutils import mongoconn as mc


def buildModel(client, input_train, output_train) :

    activation, dropout, dense, layers, optimizer, loss, epoch = getModelDetails(client)

    initializer = tf.keras.initializers.RandomNormal(mean=0., stddev=1.)

    if len(input_train.shape)>1:
        input_size = input_train.shape[1]
    else:
        input_size = 1

    if len(output_train.shape)>1:
        output_size = output_train.shape[1]
    else:
        output_size = 1

    sequence = []

    sequence.append(keras.layers.Dense(input_size, activation=activation, kernel_initializer=initializer))

    for i in range (0, layers):
        sequence.append(keras.layers.Dropout(dropout))
        sequence.append(keras.layers.Dense(dense, activation=activation, kernel_initializer=initializer))

    sequence.append(keras.layers.Dropout(dropout))
    sequence.append(keras.layers.Dense(output_size, activation=activation, kernel_initializer=initializer))

    # sequence = [
    #     keras.layers.Dense(input_size, activation=activation, kernel_initializer=initializer),
    #     keras.layers.Dropout(dropout),
    #     keras.layers.Dense(dense, activation=activation, kernel_initializer=initializer),
    #     keras.layers.Dropout(dropout),
    #     keras.layers.Dense(dense, activation=activation, kernel_initializer=initializer),
    #     keras.layers.Dropout(dropout),
    #     keras.layers.Dense(output_size, activation=activation, kernel_initializer=initializer)
    # ]

    model = keras.Sequential(sequence)

    model.compile(optimizer=optimizer,
                  loss=loss,
                  metrics=['accuracy'])

    model.save('models/model-'+client+'.h5', model.fit(input_train, output_train, epochs=epoch))


def getModelDetails(client):

    collection = mc.getMongoConn()
    client_details = collection.find({'client': client}, {'_id': 0})
    client_details = list(client_details)

    optimizer = getOptimizer(client_details)

    return client_details[0]['activation'], client_details[0]['dropout'], client_details[0]['dense'], client_details[0]['layers'], optimizer, client_details[0]['loss'], client_details[0]['epoch']


def getOptimizer(client_details):

    if client_details[0]['optimizer'] == 'sgd':
        optimizer = tf.keras.optimizers.SGD(learning_rate=float(client_details[0]['learning_rate']), momentum=float(client_details[0]['momentum']), nesterov=client_details[0]['nesterov'])
    elif client_details[0]['optimizer'] == 'adam':
        optimizer = tf.keras.optimizers.Adam(learning_rate=float(client_details[0]['learning_rate']), beta_1=float(client_details[0]['beta_1']), beta_2=float(client_details[0]['beta_2']), epsilon=float(client_details[0]['epsilon']), amsgrad=client_details[0]['amsgrad'])
    elif client_details[0]['optimizer'] == 'adadelta':
        optimizer = tf.keras.optimizers.Adadelta(learning_rate=float(client_details[0]['learning_rate']), rho=float(client_details[0]['rho']), epsilon=float(client_details[0]['epsilon']))
    elif client_details[0]['optimizer'] == 'adagrad':
        optimizer = tf.keras.optimizers.Adagrad(learning_rate=float(client_details[0]['learning_rate']), initial_accumulator_value=float(client_details[0]['initial_accumulator_value']), epsilon=float(client_details[0]['epsilon']))
    elif client_details[0]['optimizer'] == 'adamax':
        optimizer = tf.keras.optimizers.Adamax(learning_rate=float(client_details[0]['learning_rate']), beta_1=float(client_details[0]['beta_1']), beta_2=float(client_details[0]['beta_2']), epsilon=float(client_details[0]['epsilon']))
    elif client_details[0]['optimizer'] == 'ftrl':
        optimizer = tf.keras.optimizers.Ftrl(learning_rate=float(client_details[0]['learning_rate']), learning_rate_power=float(client_details[0]['learning_rate_power']), initial_accumulator_value=float(client_details[0]['initial_accumulator_value']), l1_regularization_strength=float(client_details[0]['l1_regularization_strength']), l2_regularization_strength=float(client_details[0]['l2_regularization_strength']), l2_shrinkage_regularization_strength=float(client_details[0]['l2_shrinkage_regularization_strength']))
    elif client_details[0]['optimizer'] == 'nadam':
        optimizer = tf.keras.optimizers.Nadam(learning_rate=float(client_details[0]['learning_rate']), beta_1=float(client_details[0]['beta_1']), beta_2=float(client_details[0]['beta_2']), epsilon=float(client_details[0]['epsilon']))
    elif client_details[0]['optimizer'] == 'rmsprop':
        optimizer = tf.keras.optimizers.RMSprop(learning_rate=float(client_details[0]['learning_rate']), rho=float(client_details[0]['rho']), momentum=float(client_details[0]['momentum']), epsilon=float(client_details[0]['epsilon']), centered=client_details[0]['centered'])

    # if optimizer == 'sgd':
    #     optimizer = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.0, nesterov=True)
    # elif optimizer == 'adam':
    #     optimizer = tf.keras.optimizers.Adam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07, amsgrad=True)
    # elif optimizer == 'adadelta':
    #     optimizer = tf.keras.optimizers.Adadelta(learning_rate=0.001, rho=0.95, epsilon=1e-07)
    # elif optimizer == 'adagrad':
    #     optimizer = tf.keras.optimizers.Adagrad(learning_rate=0.001, initial_accumulator_value=0.1, epsilon=1e-07)
    # elif optimizer == 'adamax':
    #     optimizer = tf.keras.optimizers.Adamax(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07)
    # elif optimizer == 'ftrl':
    #     optimizer = tf.keras.optimizers.Ftrl(learning_rate=0.001, learning_rate_power=-0.5, initial_accumulator_value=0.1, l1_regularization_strength=0.0, l2_regularization_strength=0.0, l2_shrinkage_regularization_strength=0.0)
    # elif optimizer == 'nadam':
    #     optimizer = tf.keras.optimizers.Nadam(learning_rate=0.001, beta_1=0.9, beta_2=0.999, epsilon=1e-07)
    # elif optimizer == 'rmsprop':
    #     optimizer = tf.keras.optimizers.RMSprop(learning_rate=0.001, rho=0.9, momentum=0.0, epsilon=1e-07, centered=True)

    return optimizer

