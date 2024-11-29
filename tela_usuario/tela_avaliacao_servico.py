import flet as ft
from banco.conexao2 import supabase

async def avaliar(page: ft.Page):
    if not hasattr(page, 'session_data') or not page.session_data.get('user_id'):
        page.go('/login')
        return

    servico_id = page.session_data.get('servico_selecionado')
    ordem_id = page.session_data.get('ordem_id')
    if not servico_id or not ordem_id:
        page.go('/')
        return

    try:
        servico = supabase.table('servicos')\
            .select('*, profissionais(*)')\
            .eq('id_servico', servico_id)\
            .execute()
            
        if not servico.data:
            raise Exception("Serviço não encontrado")
            
        servico_data = servico.data[0]
        profissional = servico_data['profissionais']

        ordem = supabase.table('ordens')\
            .select('*')\
            .eq('id_ordem', ordem_id)\
            .execute()
            
        if not ordem.data:
            raise Exception("Ordem não encontrada")

        pagamento = None
        if ordem.data[0]['id_pessoa_servico']:
            pagamento = supabase.table('pagamentos')\
                .select('valor')\
                .eq('id_pessoa_servico', ordem.data[0]['id_pessoa_servico'])\
                .execute()

        valor_total = pagamento.data[0]['valor'] if pagamento and pagamento.data else servico_data['valor']
        horas = int(round(valor_total / servico_data['valor'])) if servico_data['valor'] > 0 else 1
        
        selected_rating = ft.Ref[ft.Row]()
        rating_value = ft.Ref[int]()
        rating_value.current = 0
        descricao_ref = ft.Ref[ft.TextField]()

        def update_rating(index):
            rating_value.current = index + 1
            for i, star in enumerate(selected_rating.current.controls):
                star.icon = ft.icons.STAR if i <= index else ft.icons.STAR_BORDER
            page.update()

        async def enviar_avaliacao(e):
            try:
                if rating_value.current == 0:
                    print("Selecione uma avaliação")
                    return

                avaliacao = supabase.table('avaliacoes').insert({
                    'texto': descricao_ref.current.value or "Sem comentários",
                    'nota': rating_value.current,
                    'id_pessoa': page.session_data.get('user_id'),
                    'id_servico': servico_id,
                    'id_ordem': ordem_id
                }).execute()

                page.go('/conclusao-servico')

            except Exception as e:
                print(f"Erro ao enviar avaliação: {e}")

        content = ft.Column(
            controls=[
                ft.Container(
                    content=ft.Row(
                        controls=[
                            ft.Text("Avaliar o Serviço de ", size=16, font_family='Poppins Bold', color=ft.colors.BLACK),
                            ft.Text(
                                f"{profissional['nome']} {profissional['sobrenome']}", 
                                size=16, 
                                weight="bold", 
                                font_family='Poppins Medium',
                                color='#2ECC71'
                            ),
                        ],
                        alignment=ft.alignment.top_left,
                        spacing=0
                    ),
                    padding=ft.padding.only(left=15)
                ),
                ft.Container(
                    ft.Divider(thickness=1, color=ft.colors.GREY_300),
                    padding=ft.padding.only(left=15, right=15)
                ),
                ft.Column(
                    controls=[
                        ft.CircleAvatar(
                            foreground_image_url=profissional.get('avatar_url') if profissional.get('avatar_url') else None,
                            content=ft.Icon(ft.icons.PERSON) if not profissional.get('avatar_url') else None,
                            radius=40
                        ),
                        ft.Text(
                            servico_data['nome'], 
                            size=14, 
                            font_family='Poppins Regular',
                            color=ft.colors.BLACK
                        ),
                        ft.Row(
                            ref=selected_rating,
                            controls=[
                                ft.IconButton(
                                    icon=ft.icons.STAR_BORDER, 
                                    icon_color=ft.colors.YELLOW, 
                                    icon_size=32, 
                                    on_click=lambda e, i=i: update_rating(i)
                                ) for i in range(5)
                            ],
                            alignment=ft.MainAxisAlignment.CENTER,
                            spacing=2
                        )
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                ),
                ft.Divider(thickness=1, color=ft.colors.TRANSPARENT),
                ft.Row(
                    controls=[
                        ft.Text(f"R$ {valor_total:.2f}", size=16, font_family='Poppins Bold', color='#2ECC71'),
                        ft.VerticalDivider(color=ft.colors.GREY_400, width=20, thickness=1),
                        ft.Text(f"{horas} horas", size=16, font_family='Poppins Regular', color=ft.colors.BLACK),
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=5
                ),
                ft.Container(
                    ft.Divider(thickness=1, color=ft.colors.GREY_300),
                    padding=ft.padding.only(left=15, right=15)
                ),
                ft.Container(
                    content=ft.TextField(
                        ref=descricao_ref,
                        hint_text="Descrição do serviço...",
                        multiline=True,
                        min_lines=4,
                        max_lines=5,
                        filled=True,
                        bgcolor=ft.colors.WHITE,
                        width=300,
                        color='black'
                    ),
                    alignment=ft.alignment.center
                ),
                ft.Divider(thickness=1, color=ft.colors.TRANSPARENT),
                ft.Container(
                    content=ft.Row([
                        ft.ElevatedButton(
                            text="Avaliar",
                            bgcolor='#2ECC71',
                            color=ft.colors.WHITE,
                            width=150,
                            height=40,
                            style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)),
                            on_click=enviar_avaliacao
                        )
                    ], alignment=ft.MainAxisAlignment.CENTER)
                )
            ],
            scroll=ft.ScrollMode.AUTO
        )
        
        page.add(content)

    except Exception as e:
        print(f"Erro ao carregar dados: {e}")
        page.add(
            ft.Text(
                f"Erro ao carregar dados: {str(e)}",
                color="red",
                size=16,
                text_align=ft.TextAlign.CENTER
            )
        )