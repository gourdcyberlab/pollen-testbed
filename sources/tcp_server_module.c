#include <linux/kernel.h>
#include <linux/in.h>
#include <linux/kthread.h>
#include <linux/net.h>
#include <linux/socket.h>
#include <linux/syscalls.h>
#include <linux/types.h>

unsigned long **sys_call_table;

long (*pxy_sys_accept)(int, struct sockaddr __user *, int __user *);
long (*pxy_sys_bind)(int, struct sockaddr __user *, int);
long (*pxy_sys_close)(unsigned int);
long (*pxy_sys_listen)(int, int);
long (*pxy_sys_select)(int n, fd_set __user *inp, fd_set __user *outp, fd_set __user *exp, struct timeval __user *tvp);
long (*pxy_sys_setsockopt)(int fd, int level, int optname, char __user *optval, int optlen);
long (*pxy_sys_socket)(int, int, int);
long (*pxy_sys_write)(unsigned int fd, const char __user *buf, size_t count);

long svr_fd;

struct sockaddr_in svr_addr;

struct task_struct *server_task;

static unsigned long **aquire_sys_call_table(void)
{
    unsigned long int offset = PAGE_OFFSET;
    unsigned long **sct;

    while (offset < ULLONG_MAX) {
        sct = (unsigned long **)offset;

        if (sct[__NR_close] == (unsigned long *) sys_close)
            return sct;

        offset += sizeof(void *);
    }

    return NULL;
}

static int server_thread(void *data)
{
    struct sockaddr_in cli_addr;
    struct timeval timeout;
    int cli_addr_len = sizeof(cli_addr);
    int max_fd;
    int flg_on = 1;
    int rc;
    long cli_fd;
    fd_set master_set;
    fd_set working_set;

    svr_fd = pxy_sys_socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);

    memset(&svr_addr, 0, sizeof(svr_addr));
    svr_addr.sin_family = AF_INET;
    svr_addr.sin_addr.s_addr = htonl(INADDR_ANY);
    svr_addr.sin_port = htons(9090);

    if(svr_fd < 0) {
        printk(KERN_INFO "interceptor: unable to create socket\n");
        return -1;
    }

    max_fd = svr_fd;
    pxy_sys_setsockopt(svr_fd, SOL_SOCKET, SO_REUSEADDR, (char *)&flg_on, sizeof(flg_on));

    if(pxy_sys_bind(svr_fd, (struct sockaddr *)&svr_addr, sizeof(svr_addr)) < 0) {
        printk(KERN_INFO "interceptor: error binding to svr_fd\n");
        pxy_sys_close(svr_fd);
        return -1;
    }

    if(pxy_sys_listen(svr_fd, 5) < 0) {
        printk(KERN_INFO "interceptor: error listening to svr_fd\n");
        pxy_sys_close(svr_fd);
        return -1;
    }

    timeout.tv_sec  = 2;
    timeout.tv_usec = 0;

    FD_ZERO(&master_set);
    FD_SET(svr_fd, &master_set);

    while(!kthread_should_stop()) {
        memcpy(&working_set, &master_set, sizeof(master_set));

        rc = pxy_sys_select(max_fd + 1, &working_set, NULL, NULL, &timeout);

        if(rc <= 0)
            continue;

        /*
            Check if the svr_fd is ready to read
            If i have incoming data i should be checking
            the working set for each client fd and reacting
            accordingly.
        */
        if(!FD_ISSET(svr_fd, &working_set))
            continue;

        cli_fd = pxy_sys_accept(svr_fd, (struct sockaddr *) &cli_addr, &cli_addr_len);

        if(cli_fd <= 0)
            continue;

        if(cli_fd > max_fd)
            max_fd = cli_fd;

        printk(KERN_INFO "interceptor: accepted client\n");
        pxy_sys_write(cli_fd, "Hello and Goodbye.\n", 19);
        pxy_sys_close(cli_fd);
    }

    pxy_sys_close(svr_fd);
    printk(KERN_INFO "interceptor: accept loop terminated\n");

    return 0;
}

static int __init interceptor_start(void)
{
    if(!(sys_call_table = aquire_sys_call_table()))
        return -1;

    pxy_sys_accept = (void *) sys_call_table[__NR_accept];
    pxy_sys_bind = (void *)sys_call_table[__NR_bind];
    pxy_sys_close = (void *)sys_call_table[__NR_close];
    pxy_sys_listen = (void *)sys_call_table[__NR_listen];
    pxy_sys_setsockopt = (void *)sys_call_table[__NR_setsockopt];
    pxy_sys_select = (void *)sys_call_table[__NR_select];
    pxy_sys_socket = (void *)sys_call_table[__NR_socket];
    pxy_sys_write = (void *)sys_call_table[__NR_write];

    server_task = kthread_run(server_thread, NULL, "server task");

    return 0;
}

static void __exit interceptor_end(void)
{
    if(!sys_call_table)
        return;

    kthread_stop(server_task);
}

module_init(interceptor_start);
module_exit(interceptor_end);
