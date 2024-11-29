import flet as ft

def apresentacao(page : ft.Page):
    page.title = 'APRESENTACAO'

    page.bgcolor = '#FFFFFF'
    page.padding = 0

    page.fonts = {
        'Poppins Regular' : 'fonts/Poppins-Regular.ttf',
        'Poppins Medium' : 'fonts/Poppins-Medium.ttf'
    }

    profissional = ft.Container(
        ft.Image(
            src='img/profissional.png'
        ),
        alignment=ft.alignment.top_center
    )

    titulo = ft.Container(
        ft.Text(
            value='Solicite um profissional, para\nresolver problemas em\nsegundos',
            size=22,
            color='#19104E',
            font_family='Poppins Regular',
            text_align='center'
        ),
        alignment=ft.alignment.top_center,
        margin=ft.margin.only(top=-50)
    )

    subtitulo = ft.Container(
        ft.Text(
            value='O aplicativo mais rápido para reservar um\nserviço em qualquer lugar',
            size=14,
            font_family='Poppins Medium',
            color='#3B3B3B',
            text_align='center'
        ),
        alignment=ft.alignment.top_center,
        margin=ft.margin.only(top=10)
    )
    page.add(
       profissional,
       titulo,
       subtitulo
    )