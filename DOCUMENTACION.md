# Documentación Trabajo Práctico Metodología

## Grupo 8

### Integrantes

- Correa, Damián.
- Ortiz, Ignacio.
- Servetti, Emilio.
- Zárate, Lautaro.

## Resumen de cambios por sprint

### Sprint 1

- **Registrar cliente:** se implementó la página de registro con las validaciones necesarias para los campos obligatorios y los formatos correctos.
- **Inicio de sesión:** se implementó la página de inicio de sesión con email y contraseña para usuarios regulares (no administradores).
- **Visualización de productos:** se creó una *landing page* que muestra los productos con su imagen, nombre y precio.
- **Panel de administrador:** se creó un panel de administración accesible únicamente a través de un *login* para administradores.
- **Administración de productos:** se agregaron formularios para la creación y edición de productos dentro del panel de administración.

### Sprint 2

- **Botón para agregar al carrito:** se incorporó en cada producto mostrado en la *landing page*.
- **Carrito de compras:** se agregó la página del carrito, que muestra cada producto con su información, su cantidad, un *input* para modificarla y un botón para eliminarlo del carrito.
- **Panel de vendedor:** se agregó un panel disponible únicamente para los usuarios con rol "vendedor".
- **Tabla de stocks:** se incorporó al panel de vendedor, con un *input* que permite modificar el stock de cada producto.
- **Página de finalización de compra:** se agregó un botón en el carrito que redirige a la página de finalización de compra. Allí se muestra un resumen de la operación y, al presionar el botón de finalizar, la compra se guarda con estado "pendiente" y se actualiza el stock de los productos afectados.

### Sprint 3

- **Reporte de stock mínimo:** se agregó una pantalla al panel de administrador que muestra los productos por debajo del stock mínimo (configurable). Cada producto cuenta con un botón para modificar su stock y, además, se incluye un botón para descargar el reporte de stock en formato *CSV*.
- **Reporte de productos más vendidos:** se agregó un botón en el panel de vendedor para generar un reporte con el ranking de los productos más vendidos y su cantidad vendida, en formato *CSV*.
- **Creación de cupones de descuento:** se agregó una página al panel de vendedor para crear, activar y desactivar cupones de descuento.
- **Uso de cupones de descuento:** los usuarios pueden aplicar cupones de descuento en sus compras, siempre que estén activos y se ingrese el código correcto.
- **Importación masiva de productos:** se agregó una alternativa de importación masiva de productos para administradores, mediante un archivo en formato *JSON*.
