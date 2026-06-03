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
