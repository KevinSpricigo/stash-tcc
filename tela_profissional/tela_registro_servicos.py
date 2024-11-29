import flet as ft
from banco.conexao2 import supabase
from datetime import datetime

async def registrosServicos(page: ft.Page):
    if not hasattr(page, 'session_data'):
        page.session_data = {}
        page.go('/login')
        return

    id_profissional = page.session_data.get("user_id")
   
    if not id_profissional:
        page.go('/login')
        return

    page.fonts = {
        'Poppins Medium': 'fonts/Poppins-Medium.ttf',
        'Poppins Regular': 'fonts/Poppins-Regular.ttf'
    }
    page.bgcolor = '#FFFFFF'
    page.scroll = ft.ScrollMode.AUTO

    try:
        # Buscar ordens aceitas com todos os detalhes relacionados
        ordens = supabase.table('ordens')\
            .select('*, servicos(*), pessoas(*, endereco(*))')\
            .eq('id_profissional', id_profissional)\
            .eq('status', 'aceito')\
            .execute()

        if not ordens.data:
            page.add(
                ft.Container(
                    content=ft.Text(
                        "Nenhum serviço aceito no momento.",
                        size=16,
                        color='black',
                        text_align=ft.TextAlign.CENTER
                    ),
                    margin=ft.margin.only(top=50),
                    alignment=ft.alignment.center
                )
            )
            return

        for ordem in ordens.data:
            servico = ordem['servicos']
            pessoa = ordem['pessoas']
            endereco = pessoa['endereco']

            valor_total = servico['valor']

            if ordem.get('id_pessoa_servico'):
                pagamento = supabase.table('pagamentos')\
                    .select('valor')\
                    .eq('id_pessoa_servico', ordem['id_pessoa_servico'])\
                    .execute()
                
                if pagamento.data and pagamento.data[0].get('valor'):
                    valor_total = pagamento.data[0]['valor']

            servico_card = ft.Container(
                content=ft.Row(
                    controls=[
                        ft.Container(
                            ft.CircleAvatar(
                                foreground_image_url=pessoa.get('avatar_url') if pessoa.get('avatar_url') else None,
                                content=ft.Icon(ft.icons.PERSON) if not pessoa.get('avatar_url') else None,
                                radius=34
                            ),
                            padding=ft.padding.only(left=10, right=10)
                        ),
                        ft.Column(
                            [
                                ft.Text(
                                    value=f"{pessoa['nome']} {pessoa['sobrenome']}", 
                                    size=16, 
                                    color='black', 
                                    font_family='Poppins Medium',
                                    width=110
                                ),
                                ft.Text(
                                    value=endereco['cidade'], 
                                    size=10, 
                                    color='black', 
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=endereco['bairro'], 
                                    size=10, 
                                    color='black', 
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=endereco['rua'], 
                                    size=10, 
                                    color='black', 
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=str(endereco['numero']), 
                                    size=10, 
                                    color='black', 
                                    font_family='Poppins Regular'
                                ),
                            ],
                            spacing=0.5
                        ),
                        ft.VerticalDivider(width=1, thickness=1, color="black"),
                        ft.Column(
                            [
                                ft.Text(
                                    value=servico['nome'], 
                                    size=10, 
                                    color='black', 
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=f"1h R$ {servico['valor']:.2f}", 
                                    size=10, 
                                    color='black', 
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=f"Total R$ {valor_total:.2f}", 
                                    size=10, 
                                    color='#2ECC71', 
                                    font_family='Poppins Regular'
                                ),
                                ft.Text(
                                    value=datetime.strptime(ordem['data_pedido'], "%Y-%m-%dT%H:%M:%S.%f").strftime("%d/%m/%Y %H:%M"),
                                    size=10,
                                    color='black',
                                    font_family='Poppins Regular'
                                )
                            ],
                            alignment='center',
                            spacing=5
                        )
                    ],
                    alignment='start',
                    vertical_alignment='center'
                ),
                padding=ft.padding.symmetric(vertical=15),
                border=ft.border.all(1, ft.colors.GREY_300),
                border_radius=10,
                margin=ft.margin.only(bottom=10, left=10, right=10)
            )

            page.add(servico_card)
            
    except Exception as e:
        print(f"Erro ao carregar serviços: {e}")
        page.add(
            ft.Text(
                f"Erro ao carregar serviços: {str(e)}",
                color="red",
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        )