"""Command-line adapter for the shared instance generator."""

import os

from gen_instances import generate_instances, get_args_as_dict, init_parser


def main() -> None:
    args = get_args_as_dict(init_parser())
    args['outdir'] = os.path.abspath(args['outdir'])
    args['outname'] = os.path.basename(args['outname'])
    instances = generate_instances(args)
    print(f"Generated {len(instances)} instances in {args['outdir']}")


if __name__ == '__main__':
    main()
