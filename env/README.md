# The environment

This work is done on NERSC, so mainly using the environment there with some libraries git cloned to `~/lib/` additionally.

For the work environment of this repository, take a look at `env.sh` and then run `source env.sh`. It defines the environment variables used in this repository.

For NERSC users:
- `soft_link.sh` contains the soft links to the paths on NERSC, in the purpose of data management. The links should be there automatically once you clone this repository, if not, just run `bash soft_link.sh`. Once the soft links set up, you can find most of the data in our work. (If you meet 'Permission deny', please contact the owner.)