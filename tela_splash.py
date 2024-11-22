import flet as ft

def splash(page: ft.Page):
    page.padding = 0
   
    page.window.min_width = 380
    page.window.min_height = 828

    page.window.width = 380
    page.window.height = 828

    page.title = 'SPLASH'
    page.bgcolor = '#224632'


    page.fonts = {
        'Poppins Extra Bold' : 'fonts/Poppins-ExtraBold.ttf'
    }
    retangulo = ft.Container(
        width= page,
        height= page.window.height / 2,
        bgcolor= '#2ECC71',
        border_radius=ft.border_radius.only(bottom_left=49, bottom_right=49),
        alignment=ft.alignment.center      
    )

    logo = ft.Container(
        ft.Text(
            value='STASH',
            size=100,
            color='white',
            font_family='Poppins Extra Bold'

        ),
        alignment=ft.alignment.center,
        margin=ft.margin.only(top=50)
    )

    page.add(
        retangulo,
        logo
    )