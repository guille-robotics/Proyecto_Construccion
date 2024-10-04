# Proyecto de Construcción

## Objetivo
El objetivo de este proyecto es : [LIO-SAM](https://github.com/TixiaoShan/LIO-SAM.git).

## Resumen de Datos
Los datos leídos desde el sensor IMU incluyen:

- **Orientación (X, Y, Z, W):** 
  - Se obtiene de `xbus_data.quat` (en cuaterniones).
  
- **Velocidad Angular (X, Y, Z):** 
  - Se obtiene de `xbus_data.rot`.
  
- **Aceleración Lineal (X, Y, Z):** 
  - Se obtiene de `xbus_data.acc`.

## Lectura del IMU
Para leer los datos del IMU, puedes utilizar la siguiente biblioteca: [Xsens MTi Serial Reader](https://github.com/jiminghe/Xsens_MTi_Serial_Reader).


