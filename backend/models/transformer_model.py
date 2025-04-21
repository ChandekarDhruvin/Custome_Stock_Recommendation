from tensorflow.keras.layers import Input, Dense, LayerNormalization, MultiHeadAttention, Dropout # type: ignore
from tensorflow.keras.models import Model # type: ignore

def build_transformer_model(input_shape, num_heads=4, ff_dim=128):
    inputs = Input(shape=input_shape)
    attn_output = MultiHeadAttention(num_heads=num_heads, key_dim=input_shape[-1])(inputs, inputs)
    attn_output = Dropout(0.1)(attn_output)
    out1 = LayerNormalization(epsilon=1e-6)(inputs + attn_output)
    
    ffn_output = Dense(ff_dim, activation="relu")(out1)
    ffn_output = Dense(input_shape[-1])(ffn_output)
    ffn_output = Dropout(0.1)(ffn_output)
    out2 = LayerNormalization(epsilon=1e-6)(out1 + ffn_output)
    
    outputs = Dense(1)(out2[:, -1, :])
    model = Model(inputs=inputs, outputs=outputs)
    model.compile(optimizer='adam', loss='mean_squared_error')
    return model