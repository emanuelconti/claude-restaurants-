"""What the daily SocialPerks carousel says, and which day says what.

A carousel is the other post of the day, next to the video: a list that
owners of small local businesses want to read, save and send to a friend
who also runs one, in the style the owner pointed at on 30 October (a cover
photo with a big title, then one numbered point per slide, a photo under
the text, no faces). Two kinds of topic take turns, one a day: the business
ones (quiet hours, platforms, discounts, why nobody recommends them) and the
life ones the owner asked for the same day (routine, motivation, what it
feels like to run a place, what is in the news), which are the ones people
save and send. SocialPerks appears only on the last slide.

Spanish only: the profile posts in Spanish, for the venues in Barcelona.
Every claim is either common sense or the one figure with its source
(Nielsen, 2015). No em dashes, gender-neutral where it can be.

Each topic has a title for the cover, a line for the caption, and points:
a heading, the lines under it, and the closing line set in bold. `photos`
names the set its slides draw from (PHOTO_SETS); `countdown` numbers the
points from the highest down, for a ranking.
"""

from __future__ import annotations

import datetime as _dt
import random as _random

# The first day: the first business topic that day, the first life topic the
# next, and so on, alternating. Each list starts again, with other photos,
# once its topics are used.
EPOCH = _dt.date(2026, 10, 30)

BUSINESS = [
    dict(
        title="Las 7 diferencias entre un negocio que se llena y uno que no",
        hook="Las diferencias son pequeñas. El resultado, no.",
        points=[
            ("Las horas flojas", ["El que no se llena: las da por perdidas.", "El que se llena: les pone algo pequeño encima."], "Un martes a las 16:00 también se puede vender."),
            ("Sus clientes fieles", ["El que no se llena: les da las gracias.", "El que se llena: les da un motivo para traer a alguien."], "Tu mejor cliente ya conoce a tu próximo cliente."),
            ("La publicidad", ["El que no se llena: paga anuncios que nadie cree.", "El que se llena: deja hablar a quien ya vino."], "La gente cree a sus amigos, no a los anuncios."),
            ("Las plataformas", ["El que no se llena: deja del 15 al 35 % en cada pedido.", "El que se llena: las usa, pero no depende de ellas."], "El cliente que llega por un amigo es tuyo."),
            ("Los números", ["El que no se llena: «creo que el boca a boca funciona».", "El que se llena: sabe quién trajo a quién."], "Lo que no se mide no se puede repetir."),
            ("Los descuentos", ["El que no se llena: 30 % para todo el mundo.", "El que se llena: un detalle, solo para quien viene por un amigo."], "Regalar menos, pero a la persona correcta."),
            ("La constancia", ["El que no se llena: prueba algo una semana y lo deja.", "El que se llena: lo hace cada día hasta que es costumbre."], "El boca a boca no es un golpe de suerte. Es un hábito."),
        ],
    ),
    dict(
        title="Por qué tus clientes no te recomiendan (aunque les encantes)",
        hook="No es que no les gustes. Es que no se lo pones fácil.",
        points=[
            ("No se acuerdan a tiempo", ["Te recomiendan cuando un amigo pregunta «¿dónde?».", "Si ese día no piensan en ti, se lo lleva otro."], "Hay que estar en su bolsillo, no solo en su memoria."),
            ("No quieren parecer un anuncio", ["Nadie quiere sonar a publicidad delante de sus amigos.", "Un enlace personal se comparte como un favor."], "Que recomendar parezca un regalo, no una venta."),
            ("No tienen nada que ofrecer", ["«Ve, que está bien» se olvida.", "«Ve, que te invitan al postre» es un plan."], "Dales algo concreto que regalar."),
            ("Es demasiado complicado", ["Buscar tu perfil, copiar la dirección, explicar cómo llegar.", "Cada paso de más es una recomendación de menos."], "Un toque. Como mucho dos."),
            ("Nunca se lo has pedido", ["Parece obvio, pero casi nadie lo pide.", "El mejor momento es al pagar, cuando salen contentos."], "Pedirlo bien no molesta. Ayuda."),
            ("No ven que sirva de nada", ["Si un amigo vino gracias a ti y nadie te lo dice, no repites.", "Un gracias visible lo cambia todo."], "Lo que se agradece se repite."),
        ],
    ),
    dict(
        title="8 señales de que tu negocio depende demasiado de las plataformas",
        hook="Si te reconoces en más de tres, hay que hablar.",
        points=[
            ("La mitad de tus clientes nuevos llega por una app", ["Y si la app cambia las reglas, cambia tu mes."], "Tu crecimiento no debería tener dueño."),
            ("Pagas comisión por clientes que ya te conocían", ["Vuelven por ti, pero entran por la app.", "Y la app cobra igual."], "Pagar dos veces por el mismo cliente."),
            ("No tienes su contacto", ["Vienen, pagan y se van.", "No puedes volver a hablarles."], "Un cliente sin contacto es un cliente prestado."),
            ("Bajas precios para salir arriba", ["La app premia al que más rebaja.", "Tu margen paga la carrera."], "Competir en precio es competir hacia abajo."),
            ("Recuerdan la app, no tu nombre", ["«Lo pedí en la app» en vez de «fui a tu casa».", "Sin nombre no hay boca a boca."], "Que hablen de ti, no del canal."),
            ("Un cambio en el ranking se nota en caja", ["Bajas tres puestos y el martes está vacío.", "Sin haber hecho nada distinto."], "Tu negocio no puede depender de un algoritmo ajeno."),
            ("No sabes cuánto te cuesta un cliente nuevo", ["Entre comisiones, promos y anuncios, nadie hace la cuenta.", "Y casi siempre es más de lo que crees."], "Haz la cuenta una vez. Cambia decisiones."),
            ("No tienes un plan B", ["Si mañana desaparece la app, ¿de dónde vienen los clientes?", "Si no hay respuesta, ese es el problema."], "El mejor plan B son tus propios clientes."),
        ],
    ),
    dict(
        title="Por qué creemos a un amigo y no a un anuncio",
        hook="No es marketing. Es cómo funcionamos las personas.",
        points=[
            ("Confiamos en quien nos conoce", ["Según Nielsen (2015), el 83 % confía en lo que le recomiendan amigos y familia.", "Es la forma de publicidad en la que más se confía."], "Un amigo convence más que cualquier anuncio."),
            ("La prueba social", ["Si alguien como tú ya fue y le gustó, el riesgo parece menor.", "Copiar a los nuestros nos ahorra decisiones."], "Nadie quiere ser el primero. Todos quieren ser el segundo."),
            ("El anuncio quiere algo", ["Sabemos que el anuncio quiere vendernos.", "Del amigo esperamos la verdad."], "La confianza no se compra. Se presta."),
            ("La reciprocidad", ["Cuando alguien nos hace un favor, queremos devolverlo.", "Un detalle para quien recomienda activa ese instinto."], "Dar primero también es estrategia."),
            ("Lo concreto convence", ["«Es buenísimo» no mueve a nadie.", "«Pide el de pistacho y siéntate fuera» sí."], "Los amigos no hablan en eslóganes."),
            ("Lo cercano pesa más", ["Una reseña de un desconocido informa.", "Un mensaje de un amigo decide."], "La distancia entre informar y convencer es una persona."),
        ],
    ),
    dict(
        title="Lo que hace a las 16:00 un negocio con la agenda llena",
        hook="La diferencia no está en la hora punta. Está en la hora floja.",
        points=[
            ("Sabe cuál es su hora floja", ["No dice «a veces está tranquilo».", "Dice «los martes de 15:00 a 17:00»."], "Lo que tiene nombre se puede llenar."),
            ("Le pone un motivo", ["Un detalle pequeño, solo en esa franja.", "No un descuento para todo el día."], "Mover a la gente a otra hora es más fácil que traer gente nueva."),
            ("Usa a sus clientes fieles", ["Les da un enlace para invitar a un amigo justo en esas horas.", "Quien ya viene sabe a quién le encantaría."], "Tus clientes tienen agenda. Sus amigos también."),
            ("No espera a que suene el teléfono", ["Cada día comparte algo: una foto, un hueco libre, una historia.", "Poco, pero cada día."], "La constancia gana a la inspiración."),
            ("Mide lo que funciona", ["Sabe cuántos vinieron por un amigo y cuánto gastaron.", "Repite lo que funciona y deja el resto."], "Sin números, todo es opinión."),
            ("Cuida al que llega por primera vez", ["El primer día decide si vuelve.", "Y si vuelve con alguien."], "El cliente nuevo es tu próximo embajador."),
        ],
    ),
    dict(
        title="7 errores que dejan sillas vacías un martes por la tarde",
        hook="Casi nunca es el producto. Casi siempre es esto.",
        points=[
            ("Hacer descuentos para todos", ["Regalas margen también a quien iba a venir igual.", "Y enseñas a esperar la oferta."], "Un descuento general es caro. Un detalle bien dirigido, no."),
            ("Publicar solo cuando hay novedades", ["Las redes premian la constancia.", "Si apareces una vez al mes, te olvidan."], "Poco y cada día gana a mucho y a veces."),
            ("Esperar que te recomienden solos", ["Les encantas, pero no saben cómo ayudarte.", "Dales un enlace y un motivo."], "El boca a boca se puede provocar."),
            ("Pagar anuncios sin medir", ["Clics, alcance, impresiones.", "¿Pero cuántos clientes entraron por la puerta?"], "Paga por clientes, no por miradas."),
            ("Olvidarte del cliente que ya vino", ["Conseguir uno nuevo cuesta más que hacer volver al que ya vino.", "Y ese ya confía en ti."], "Tu mejor canal ya está sentado en tu local."),
            ("Llenar solo las horas punta", ["El sábado se llena solo.", "El martes a las 16:00 es donde está el dinero que te falta."], "Mira las horas, no solo los días."),
            ("No saber de dónde viene cada cliente", ["Si no lo sabes, no puedes repetirlo.", "Ni dejar de pagar lo que no funciona."], "Pregunta, apunta, mide."),
        ],
    ),
    dict(
        title="Descuento o regalo: por qué el 30 % te sale caro",
        hook="Parece lo mismo. En tu caja, no.",
        points=[
            ("El descuento es para todos", ["También para quien iba a venir igual.", "Pierdes margen sin ganar clientes."], "Un descuento general paga a los que ya tenías."),
            ("El descuento educa mal", ["El cliente aprende a esperar la oferta.", "Y el precio normal empieza a parecer caro."], "Lo que regalas siempre deja de valer."),
            ("El regalo es concreto", ["Un postre, un arreglo de barba, una clase.", "Se recuerda y se cuenta."], "Nadie presume de un 30 %. Sí de un regalo."),
            ("El regalo cuesta menos", ["Te cuesta lo que cuesta producirlo, no lo que vale en carta.", "Y el cliente lo valora a precio de carta."], "Mismo efecto, menos coste."),
            ("El regalo se puede dirigir", ["Solo a quien viene por un amigo.", "Solo en tus horas flojas."], "Regala donde lo necesitas, no en todas partes."),
            ("El regalo genera historia", ["«Me invitaron al postre» se comparte.", "«Tenía un 30 %» no."], "Lo que se cuenta trae a otros."),
        ],
    ),
    dict(
        title="El cliente de 1 visita, el de 3 y el de 10: qué cambia",
        hook="Cada visita cambia lo que puede hacer por ti.",
        points=[
            ("1 visita", ["Vino por curiosidad o por casualidad.", "Todavía compara contigo a otros tres sitios."], "Aquí se decide si vuelve."),
            ("2 visitas", ["Le gustó lo suficiente para repetir.", "Empieza a tener su sitio, su silla, su plato."], "Hazle sentir que lo recuerdas."),
            ("3 visitas", ["Ya es cliente.", "Habla de ti cuando sale el tema."], "Es el momento de darle algo que compartir."),
            ("5 visitas", ["Ya no compara.", "Te defiende si alguien te critica."], "Pídele que traiga a alguien. Dirá que sí."),
            ("10 visitas", ["Es parte del sitio.", "Sus amigos ya saben dónde va."], "Tu mejor publicidad. Trátalo como tal."),
            ("La conclusión", ["Llenar un negocio no es solo atraer gente nueva.", "Es ayudar a cada cliente a subir un escalón."], "Y que cada uno traiga al siguiente."),
        ],
    ),
    dict(
        title="Cuánto te cuesta de verdad un cliente nuevo",
        hook="Haz esta cuenta una vez. Cambia cómo gastas.",
        points=[
            ("Los anuncios", ["Pagas por clics y por alcance.", "No sabes cuántos entraron por la puerta."], "Pagas por miradas, no por clientes."),
            ("Las plataformas", ["Entre un 15 y un 35 % de cada pedido o reserva.", "También del cliente que vuelve."], "Pagas cada vez, no una vez."),
            ("Los descuentos", ["Lo pierdes también con quien iba a venir igual.", "El coste real es mayor de lo que parece."], "El descuento más caro es el que no hacía falta."),
            ("Los flyers", ["Imprimir, repartir y esperar.", "Casi imposible saber qué funcionó."], "Lo que no se mide no se mejora."),
            ("El boca a boca de siempre", ["Casi gratis y el que más confianza da.", "Pero no lo controlas ni lo puedes contar."], "El mejor canal, si lo pudieras medir."),
            ("El boca a boca medido", ["Tus clientes comparten su enlace, sus amigos vienen.", "Pagas solo cuando llega alguien nuevo y paga."], "La confianza de un amigo, con números."),
        ],
    ),
    dict(
        title="6 cosas que tus mejores clientes harían por ti si se lo pidieras",
        hook="Casi nunca se lo pedimos. Casi siempre dicen que sí.",
        points=[
            ("Traer a un amigo", ["Ya conocen a gente a la que le encantaría tu sitio.", "Solo necesitan un motivo y un enlace."], "Tu próximo cliente está en su WhatsApp."),
            ("Subir una Story", ["Una foto en tu local, en el mejor momento.", "Sus amigos la ven y preguntan «¿dónde?»."], "Una Story de un cliente vale más que diez tuyas."),
            ("Venir en tu hora floja", ["Si les da igual el día, elegirán el que te ayuda.", "Pero tienen que saber cuál es."], "Díselo. Muchos te harán el favor."),
            ("Contarte qué mejorar", ["Saben lo que nadie te dice.", "Y te lo dirán con cariño si preguntas."], "Tus fieles son tu mejor consultor."),
            ("Dejar una reseña", ["Les cuesta un minuto.", "A ti te trae clientes durante años."], "Pídela al pagar, no por email una semana después."),
            ("Defenderte", ["Cuando alguien te critica, salen a hablar por ti.", "Porque te sienten suyo."], "Cuida a los que te cuidan."),
        ],
    ),
    dict(
        title="Por qué las reseñas ya no bastan",
        hook="Las reseñas informan. Los amigos deciden.",
        points=[
            ("Todos tienen 4,7 estrellas", ["Cuando todos puntúan alto, la nota ya no distingue.", "El cliente necesita otra señal."], "Si todos son buenos, nadie destaca."),
            ("Son de desconocidos", ["No sabes quién escribió ni qué le gusta.", "Un amigo sí sabe lo que te gusta a ti."], "La opinión que importa es la de alguien cercano."),
            ("Llegan tarde", ["Se leen cuando ya se está buscando.", "La recomendación de un amigo crea las ganas."], "Una reseña responde. Un amigo provoca."),
            ("No traen a nadie", ["Ayudan a decidir entre opciones.", "No hacen que alguien piense en ti."], "Las reseñas convencen. No invitan."),
            ("Se pueden comprar", ["Y la gente lo sabe.", "Por eso las mira con desconfianza."], "Lo que no se puede comprar vale más."),
            ("Lo que sí funciona", ["Reseñas para que te encuentren.", "Amigos para que te elijan."], "Usa las dos. Pero mide la segunda."),
        ],
    ),
    dict(
        title="5 frases que matan el boca a boca sin que te des cuenta",
        hook="Las decimos con buena intención. Y cierran puertas.",
        points=[
            ("«Ya nos conocen»", ["Te conocen los que ya vienen.", "Sus amigos todavía no."], "Cada cliente tiene un círculo que aún no te ha probado."),
            ("«El boca a boca no se puede controlar»", ["No se puede forzar, pero sí facilitar.", "Un enlace, un motivo, el momento justo."], "Lo que se facilita, pasa más."),
            ("«No quiero molestar a mis clientes»", ["Pedir con gusto no molesta.", "Lo que molesta es que te lo pidan mal o a deshora."], "Al pagar, contentos, con algo que regalar."),
            ("«Ya hacemos redes»", ["Tus redes las ven tus seguidores.", "Las de tus clientes las ven sus amigos."], "Tus clientes tienen más alcance que tú."),
            ("«Ya probamos un programa de puntos»", ["Nadie quiere más puntos ni más tarjetas.", "Quieren algo que compartir con un amigo."], "La fidelidad se cuenta en amigos, no en puntos."),
        ],
    ),
    dict(
        title="Cómo convertir a un cliente contento en tu mejor embajador",
        hook="No hace falta una agencia. Hace falta un sistema.",
        points=[
            ("Elige el momento", ["Al pagar, cuando sale contento.", "No por email una semana después."], "El entusiasmo dura minutos. Aprovéchalos."),
            ("Dale algo que regalar", ["Un detalle para su amigo, no para él.", "Así recomendar es hacer un favor."], "Nadie presume de pedir. Todos de regalar."),
            ("Ponlo fácil", ["Un enlace que comparte en un toque.", "Por Story o por mensaje, como quiera."], "Cada paso de más es un amigo de menos."),
            ("Dirige la visita", ["Que el regalo sea en tus horas flojas.", "Así cada amigo llena un hueco."], "Llena las horas que te faltan, no las que ya tienes."),
            ("Agradécelo", ["Cuando el amigo viene, quien lo trajo se entera.", "Y recibe su recompensa."], "Lo que se agradece se repite."),
            ("Mídelo", ["Quién trajo a quién, cuándo y cuánto gastó.", "Así sabes qué repetir."], "Embajadores, no casualidades."),
        ],
    ),
    dict(
        title="Las horas vacías no se llenan solas: 6 ideas para la tuya",
        hook="La hora más difícil de tu semana tiene arreglo.",
        points=[
            ("Ponle nombre", ["«Martes de 15:00 a 17:00», no «a veces está flojo».", "Lo que tiene nombre se puede trabajar."], "Primero localiza el hueco."),
            ("Un detalle solo en esa franja", ["Un postre, una mascarilla, una clase extra.", "Pequeño, pero solo ahí."], "Mueve a la gente sin rebajar tu precio."),
            ("Díselo a los fieles", ["Muchos pueden venir cuando quieran.", "Si saben qué hora te ayuda, la eligen."], "Tus clientes quieren ayudarte. Diles cómo."),
            ("Invita a sus amigos", ["Un enlace para traer a alguien justo en esa hora.", "El amigo llega con un regalo, tú llenas el hueco."], "Dos personas nuevas en tu peor hora."),
            ("Enséñalo cada día", ["Una Story: «hoy a las 16:00 hay hueco».", "Lo verá quien puede venir."], "La gente no viene a lo que no sabe que existe."),
            ("Mide una semana", ["Cuántos vinieron y por qué.", "Repite lo que funcionó."], "Cada semana un poco más llena."),
        ],
    ),
]

# Unsplash photos without faces to camera, by what they show; each id was
# fetched and looked at (30 October). "venue" is the video's own photos.
PHOTO_SETS = {
    "life": [
        "1470252649378-9c29740c9fa8",  # sunrise over a valley
        "1501139083538-0139583c060f",  # hourglass
        "1495364141860-b0d03eccd065",  # a hand holding an alarm clock
        "1484480974693-6ca0a78fb36b",  # an open notebook
        "1506784983877-45594efa4cbe",  # a planner and a coffee
        "1434030216411-0b793f4b4173",  # a hand writing
        "1488190211105-8b0e65b80b4e",  # a desk, a coffee, a journal
        "1506126613408-eca07ce68773",  # a silhouette at sunrise
        "1447752875215-b2761acb3c5d",  # a bridge into the woods
        "1511920170033-f8396924c348",  # latte art, beans, from above
        "1509042239860-f550ce710b93",  # three cappuccinos
        "1442975631115-c4f7b05b8a2c",  # a café inside, morning light
    ],
    "money": [
        "1554224155-6726b3ff858f",  # hands with receipts
        "1563013544-824ae1b704d3",  # a card in a hand
        "1520607162513-77705c0f0d4a",  # a card terminal, from above
        "1519389950473-47ba0277781c",  # a desk full of laptops, from above
        "1486312338219-ce68d2c6f44d",  # hands typing
        "1516321318423-f06f85e504b3",  # a hand at a laptop
        "1484480974693-6ca0a78fb36b",  # an open notebook
        "1434030216411-0b793f4b4173",  # a hand writing
        "1488190211105-8b0e65b80b4e",  # a desk, a coffee, a journal
    ],
    "city": [
        "1583422409516-2895a77efded",  # Barcelona from above
        "1511527661048-7fe73d85e9a4",  # Tibidabo at dusk
        "1517248135467-4c7edcad34c4",  # a restaurant inside
        "1554118811-1e0d58224f24",  # a café, empty chairs
        "1521017432531-fbd92d768814",  # a café counter
        "1493857671505-72967e2e2760",  # a café with a menu board and a bike
        "1524758631624-e2822e304c36",  # a lounge with armchairs
        "1497935586351-b67a49e012bf",  # coffee beans on a board
        "1510812431401-41d2bd2722f3",  # wine glasses raised
        "1528712306091-ed0763094c98",  # hands at the stove
    ],
}

LIFE = [
    dict(
        title="Ranking de los 8 peores momentos de tener un negocio",
        hook="Si tienes un negocio, los has vivido todos.",
        photos="life", countdown=True,
        points=[
            ("Mirar la agenda del martes", ["Huecos a las 16:00, a las 17:00, a las 18:00.", "Y el alquiler no tiene huecos."], "La hora vacía también se paga."),
            ("El proveedor sube precios otra vez", ["Tú no puedes subir los tuyos cada mes.", "La diferencia sale de tu bolsillo."], "El margen se gana en los detalles."),
            ("La reseña injusta", ["Una estrella de alguien que vino un día malo.", "Y la leen todos los que vienen detrás."], "Por eso importa tanto lo que cuentan los que sí te quieren."),
            ("El empleado que no viene", ["Sábado, local lleno, un hueco en la barra.", "Y tú haciendo de tres."], "Nadie te enseña esto antes de abrir."),
            ("Pagar la comisión de la app", ["Ves el pedido y ves lo que se queda la plataforma.", "Por un cliente que quizá ya te conocía."], "Trabajar para otro sin saberlo."),
            ("El domingo por la noche", ["El cuerpo descansa, la cabeza no.", "Ya estás pensando en el lunes."], "Tener un negocio no tiene horario de cierre."),
            ("Cerrar la caja y no salen las cuentas", ["Un buen día que no lo fue tanto.", "Haces números otra vez, por si acaso."], "Saber de dónde viene cada euro cambia el sueño."),
            ("El cliente fiel que deja de venir", ["Venía cada semana. Un día, nada.", "Y no sabes por qué."], "Cuida a los que ya te eligieron."),
        ],
    ),
    dict(
        title="La rutina de los dueños que aguantan 20 años abiertos",
        hook="No es suerte. Es rutina.",
        photos="life",
        points=[
            ("Empiezan antes de abrir", ["Media hora sin clientes y sin móvil.", "Para pensar el día, no para sobrevivirlo."], "El día que empieza con plan termina mejor."),
            ("Miran los números cada semana", ["No cada noche con angustia.", "Una vez por semana, con calma, siempre el mismo día."], "Lo que se mira con calma se arregla."),
            ("Conocen a sus clientes por el nombre", ["Y saben qué piden.", "Eso no lo copia ninguna cadena."], "La cercanía es tu ventaja."),
            ("Cambian poco, pero siempre", ["Un plato nuevo, un horario mejor, una idea al mes.", "Sin revolucionar nada."], "Mejorar un poco, siempre."),
            ("Descansan de verdad", ["Un día a la semana sin pensar en el local.", "El que no para, se quema."], "Tu negocio necesita que estés bien."),
            ("Dejan que sus clientes hablen por ellos", ["No gritan en redes.", "Hacen que sus clientes quieran contarlo."], "El que dura es el que recomiendan."),
        ],
    ),
    dict(
        title="Las 7 sensaciones que solo entiende quien tiene un negocio",
        hook="Las buenas compensan todas las demás.",
        photos="city",
        points=[
            ("El primer cliente del día", ["Abres la puerta y ya hay alguien esperando.", "El día empieza bien."], "Pequeñas victorias, cada mañana."),
            ("Ver tu local lleno", ["Todas las mesas, todas las sillas.", "Y piensas: esto lo he hecho yo."], "Merece la pena por momentos así."),
            ("El cliente que vuelve con un amigo", ["No hay mejor reseña.", "Te ha elegido dos veces: una para él y otra para alguien que quiere."], "La recomendación es el mayor cumplido."),
            ("Un «gracias» de verdad", ["De alguien que se va contento.", "Te dura toda la tarde."], "Por eso abriste."),
            ("«¿Esto es tuyo?»", ["Lo dice alguien con admiración.", "Y te acuerdas de todo lo que costó."], "Lo construiste tú."),
            ("Cerrar con las cuentas bien", ["Bajar la persiana tranquilo.", "Saber que el mes está cubierto."], "La tranquilidad también es un logro."),
            ("Que te reconozcan por la calle", ["«Tú eres el del café de la esquina.»", "Ya eres parte del barrio."], "Un negocio local es un lugar en la vida de la gente."),
        ],
    ),
    dict(
        title="Lo que nadie te cuenta antes de abrir tu propio negocio",
        hook="Ojalá alguien me lo hubiera dicho antes.",
        photos="money",
        points=[
            ("Vender es la mitad del trabajo", ["Hacer bien lo tuyo no basta.", "Que la gente lo sepa es otro trabajo."], "El mejor producto escondido no vende."),
            ("Los primeros meses son los más lentos", ["La gente tarda en descubrirte.", "No es que no funcione: es que aún no te conocen."], "Paciencia y constancia."),
            ("Tus primeros clientes valen oro", ["Ellos traen a los siguientes.", "Trátalos como socios, no como tickets."], "Tus primeros fieles construyen tu fama."),
            ("Los números mandan", ["El local puede estar lleno y perder dinero.", "Mira margen, no solo caja."], "Lleno no siempre es rentable."),
            ("Vas a hacer de todo", ["Contable, limpieza, marketing, recursos humanos.", "Aprende a pedir ayuda pronto."], "Hacerlo todo no es lo mismo que hacerlo bien."),
            ("Merece la pena", ["Es duro, pero es tuyo.", "Y cada cliente que vuelve te lo recuerda."], "Nadie se arrepiente de haberlo intentado."),
        ],
    ),
    dict(
        title="El alquiler sube y los clientes no: 6 formas de aguantar",
        hook="El tema del que habla todo el barrio.",
        photos="city",
        points=[
            ("Llena las horas que ya pagas", ["El alquiler cuesta lo mismo a las 16:00 que a las 21:00.", "Cada hora vacía es dinero perdido."], "Empieza por tus horas flojas."),
            ("Haz que cada cliente traiga a otro", ["Conseguir un cliente nuevo por un amigo cuesta menos que con anuncios.", "Y suele quedarse más."], "Tus clientes son tu mejor canal."),
            ("Revisa lo que pagas cada mes", ["Comisiones, suscripciones, herramientas que no usas.", "Una tarde de revisión puede ahorrarte mucho."], "Lo pequeño, sumado, es grande."),
            ("Sube el ticket, no el precio", ["Un postre sugerido, un tratamiento extra.", "Sin tocar la carta."], "Vender mejor, no más caro."),
            ("Únete a tus vecinos", ["Los negocios del barrio tienen los mismos clientes.", "Recomendarse entre vosotros os ayuda a todos."], "El barrio es un equipo."),
            ("No compitas con las cadenas en precio", ["Compite en lo que no pueden copiar.", "El trato, el nombre, la cercanía."], "Lo local se elige, no se compara."),
        ],
    ),
    dict(
        title="8 señales de que estás construyendo algo que vale la pena",
        hook="Para los días en que dudas.",
        photos="life",
        points=[
            ("Tienes clientes que repiten", ["No vuelven por obligación.", "Vuelven porque quieren."], "Repetir es votar por ti."),
            ("Te recomiendan sin que lo pidas", ["Alguien llega diciendo «me ha dicho una amiga».", "Esa es la mejor señal que existe."], "El boca a boca no miente."),
            ("Sabes el nombre de tus clientes", ["Y ellos saben el tuyo.", "Eso no se consigue con publicidad."], "Has creado comunidad."),
            ("Aprendes algo cada semana", ["Un error que no repites, una idea que funciona.", "Eso es crecer."], "El progreso no siempre se ve en caja."),
            ("Te cuesta desconectar", ["Porque te importa.", "Ahora aprende a descansar también."], "Te importa. Cuídate para seguir."),
            ("Tu equipo se queda", ["La gente no se queda en sitios donde no está bien.", "Si se quedan, algo haces bien."], "Un buen equipo es un buen negocio."),
            ("Los malos días ya no te hunden", ["Sabes que pasan.", "Y que mañana vuelves a abrir."], "La constancia es tu superpoder."),
            ("Todavía te ilusiona abrir", ["Después de todo, sigues queriendo.", "No todo el mundo puede decirlo."], "Sigue. Va bien."),
        ],
    ),
    dict(
        title="Lo que la IA no puede hacer por tu negocio (y tus clientes sí)",
        hook="Todo el mundo habla de la IA. Hablemos de lo que no cambia.",
        photos="money",
        points=[
            ("Recomendarte a un amigo", ["La IA puede escribir un anuncio.", "No puede decirle a su mejor amiga «tienes que ir»."], "La confianza no se genera. Se gana."),
            ("Acordarse de cómo te gusta el café", ["El detalle de quien te conoce.", "Eso no se automatiza."], "Lo humano es tu ventaja."),
            ("Hacer que alguien se sienta en casa", ["Un saludo por tu nombre al entrar.", "Ninguna app lo sustituye."], "La gente vuelve por cómo la tratas."),
            ("Vivir el barrio", ["Saber qué pasa en la calle, quién es quién.", "Eso solo lo sabe quien está."], "Lo local no se descarga."),
            ("Donde sí te ayuda", ["A escribir más rápido, a ordenar números, a ahorrar tiempo.", "Úsala para tener más tiempo para tus clientes."], "Máquinas para las tareas. Personas para las personas."),
        ],
    ),
]


CAPTION_TAIL = (
    "Guárdalo para cuando lo necesites y mándaselo a alguien que tenga un negocio.\n\n"
    "SocialPerks convierte a tus clientes en embajadores. Sin cuota mensual: solo pagas por clientes nuevos que pagan. socialperkses.com"
)
HASHTAGS = "#negociolocal #emprendedores #marketinglocal #bocaaboca #pymes #barcelona #hosteleria #peluqueria"

CTA = dict(
    title="Convierte a tus clientes en embajadores.",
    lines=["Comparten su enlace. Sus amigos vienen.", "Tú sabes quién trajo a quién."],
    small="Sin cuota mensual. Solo pagas por clientes nuevos que pagan.",
    url="socialperkses.com",
)


SLOTS = 3  # carousels a day (the owner, 30 October: "almeno 2 o 3 al giorno")


def check_topic(topic: dict) -> list:
    """What is wrong with a topic written for a run, in words a writer can fix; empty if nothing."""
    errors = []
    def text(value, name, most):
        if not isinstance(value, str) or not value.strip():
            errors.append(f"{name} is missing")
        elif len(value) > most:
            errors.append(f"{name} has {len(value)} characters, at most {most}: {value!r}")
        elif "\u2014" in value or "\u2013" in value:
            errors.append(f"{name} has a dash; use a colon, a full stop or a comma: {value!r}")
        elif "perk" in value.lower() and "socialperks" not in value.lower():
            errors.append(f"{name} says 'perk', never used in Spanish copy: {value!r}")
    text(topic.get("title"), "title", 90)
    text(topic.get("hook"), "hook", 120)
    points = topic.get("points")
    if not isinstance(points, list) or not 5 <= len(points) <= 8:
        errors.append("points must be a list of 5 to 8 points")
        points = []
    for i, point in enumerate(points, 1):
        if not (isinstance(point, (list, tuple)) and len(point) == 3 and isinstance(point[1], list)):
            errors.append(f"point {i} must be [heading, [line, line], closing line]")
            continue
        heading, lines, punch = point
        text(heading, f"point {i} heading", 52)
        if not 1 <= len(lines) <= 2:
            errors.append(f"point {i} needs 1 or 2 lines")
        for j, line in enumerate(lines, 1):
            text(line, f"point {i} line {j}", 95)
        text(punch, f"point {i} closing line", 75)
    if topic.get("photos", "venue") not in list(PHOTO_SETS) + ["venue"]:
        errors.append(f"photos must be one of {sorted(PHOTO_SETS) + ['venue']}")
    return errors


def bank_topic(date: _dt.date, slot: int = 1) -> dict:
    """A written topic for a date and slot, when a run has none of its own: business and life take turns."""
    n = (date - EPOCH).days * SLOTS + (slot - 1)
    return BUSINESS[(n // 2) % len(BUSINESS)] if n % 2 == 0 else LIFE[(n // 2) % len(LIFE)]


def carousel(date: _dt.date, venue_photos: list, slot: int = 1, topic: dict | None = None) -> dict:
    """The slides' content for a date and slot, with one photo per slide (cover first), the same every time."""
    topic = topic or bank_topic(date, slot)
    rng = _random.Random(date.toordinal() * 10 + slot)
    pool = list(PHOTO_SETS.get(topic.get("photos"), venue_photos))
    rng.shuffle(pool)
    need = 1 + len(topic["points"])
    picks = (pool * (need // len(pool) + 1))[:need]
    # The title opens the caption, so the next runs can see what was already posted.
    caption = f"{topic['title']}\n\n{topic['hook']}\n\n{CAPTION_TAIL}\n\n{HASHTAGS}"
    count = len(topic["points"])
    numbers = list(range(count, 0, -1)) if topic.get("countdown") else list(range(1, count + 1))
    return dict(date=date.isoformat(), slot=slot, title=topic["title"], points=topic["points"], numbers=numbers, photos=picks, caption=caption)
