# 引入 transitions 库里的核心类
from transitions import Machine


class Order:
    # 定义状态集
    states = ['created', 'paid', 'delivering', 'received', 'done', 'cancelling', 'returning', 'closed']

    def __init__(self, order_id):
        self.order_id = order_id

        # 创建 FSM
        self.machine = Machine(model=self, states=Order.states, initial='created')

        # 定义状态转换函数
        # 基本的语法很好懂，trigger 参数是输入函数名，source 和 dest 分别是当前和转换后的状态
        # before 参数表示进行这个状态转换之前要调用的函数，如果该函数运行时出现异常，状态转换会中止
        self.machine.add_transition(trigger='t_pay', source='created', dest='paid', before='payment_service')
        # after 参数表示当这个状态转换完成后调用的函数，我们用这个函数来通知用户已经发货在途了
        self.machine.add_transition(trigger='t_deliver', source='paid', dest='delivering', after='notify_delivering')
        self.machine.add_transition(trigger='t_receive', source='delivering', dest='received')
        self.machine.add_transition(trigger='t_confirm', source='received', dest='done')
        # 可以一次定义多个状态向同一个状态的装换
        self.machine.add_transition(trigger='t_cancel', source=['created', 'paid'], dest='cancelling')
        self.machine.add_transition(trigger='t_return', source=['delivering', 'received'], dest='returning')
        self.machine.add_transition(trigger='t_close', source=['cancelling', 'returning'], dest='closed')

    def payment_service(self):
        print('支付服务申请中……')
        # 调用远程接口完成实际支付，如果失败可抛出异常，对应的状态转换会中止（即，不会转换到 'paid' 状态）
        return

    def notify_delivering(self):
        # 通知用户已发货在途
        print('已通知用户：商品配送中')
        return

# 然后就可以测试一下了
order1 = Order(1)
order1.state # => 'created'
# order1.t_receive() # => 如果运行这一句会抛出 MachineError 异常，因为当前状态与此 trigger（输入）不匹配，转换不被允许
order1.t_pay() # => 会先调用 payment_service()，成功的话返回 True
order1.state # => 'paid'
order1.t_deliver() # => 成功后调用 notify_delivering() 通知用户
order1.t_receive()
order1.t_confirm()
order1.state # => 'done'