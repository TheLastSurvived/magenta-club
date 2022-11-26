from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqlamodel import ModelView
from .models import User,News,Service,Orders
from app import app,db
from flask_admin import Admin
from flask import make_response,session,abort

class AdminIndex(AdminIndexView):
    @expose('/', methods=['GET', 'POST'])
    def index(self):
        if 'name' in session:
            user = User.query.filter_by(email=session['name']).first()
            if user.root!=1:
                abort(403)
            else:
                return self.render('admin/dashboard_index.html')
        else:
            abort(401)


admin = Admin(app, name='Magenta', template_mode='bootstrap3',index_view=AdminIndex())



class OrdersView(ModelView):
    column_display_pk = True 
    column_hide_backrefs = False
    column_list = ['id','price','date','service_name','service_type','qr_image','qr_image_name','user_id']

admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(News, db.session))
admin.add_view(ModelView(Service, db.session))
admin.add_view(OrdersView(Orders, db.session))