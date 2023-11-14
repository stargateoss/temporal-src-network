from ...logger.logger_core import logger

LOG_TAG = "git_ref_utils"

TAGS_REF_SPEC = "+refs/tags/*:refs/tags/*"

def get_checkout_info(git, ref, commit):
    if not git:
        logger.error(LOG_TAG, "The 'git' arg for 'get_checkout_info' method not set ")
        return (1, None, None)

    if not ref and not commit:
        logger.error(LOG_TAG, "The 'ref' and 'commit' args for 'get_checkout_info' method cannot both be unset")
        return (1, None, None)

    checkout_ref = None
    checkout_start_point = None
    upper_ref = ref.upper() if ref else ""

    # SHA only
    if not ref:
        checkout_ref = commit
    # refs/heads/
    elif upper_ref.startswith('REFS/HEADS/'):
        branch = ref[len("refs/heads/"):]
        checkout_ref = branch
        checkout_start_point = "refs/remotes/origin/" + branch
    # refs/pull/
    elif upper_ref.startswith('REFS/PULL/'):
        branch = ref[len("refs/pull/"):]
        checkout_ref = "refs/remotes/pull/" + branch
    # refs/tags/
    elif upper_ref.startswith('REFS/'):
        checkout_ref = ref
    # Unqualified ref, check for a matching branch or tag
    else:
        if git.branch_exists(True, "origin/" + ref):
            checkout_ref = ref
            checkout_start_point = "refs/remotes/origin/" + ref
        elif git.tag_exists(ref):
            checkout_ref = "refs/tags/" + ref
        else:
            logger.error(LOG_TAG, "A branch or tag with the name '" + ref + "' could not be found")
            return (1, None, None)

    return (0, checkout_ref, checkout_start_point)



def get_ref_spec_for_all_history(ref, commit):
    ref_spec = ['+refs/heads/*:refs/remotes/origin/*', TAGS_REF_SPEC]
    if ref and ref.upper().startswith('REFS/PULL/'):
        branch = ref[len("refs/pull/"):]
        ref = commit if commit else ref
        ref_spec.append("+" + ref + ":refs/remotes/pull/" + branch)

    return ref_spec



def get_ref_spec(ref, commit):
    if not ref and not commit:
        logger.error(LOG_TAG, "The 'ref' and 'commit' args for 'get_ref_spec' method cannot both be unset")
        return (1, None)

    upper_ref = ref.upper() if ref else ""
    ref_spec = None

    # SHA
    if commit:
        # refs/heads
        if upper_ref.startswith('REFS/HEADS/'):
            branch = ref[len("refs/heads/"):]
            ref_spec = ["+" + commit + ":refs/remotes/origin/" + branch]
        # refs/pull/
        elif upper_ref.startswith('REFS/PULL/'):
            branch = ref[len("refs/pull/"):]
            ref_spec = ["+" + commit + ":refs/remotes/pull/" + branch]
        # refs/tags/
        elif upper_ref.startswith('REFS/TAGS/'):
            ref_spec = ["+" + commit + ":" + ref]
        # Otherwise no destination ref
        else:
            ref_spec = [commit]

    # Unqualified ref, check for a matching branch or tag
    elif not upper_ref.startswith('REFS/'):
        ref_spec = [
            "+refs/heads/" + ref + "*:refs/remotes/origin/" + ref + "*",
            "+refs/tags/" + ref + "*:refs/tags/" + ref + "*"
        ]
    # refs/heads/
    elif upper_ref.startswith('REFS/HEADS/'):
        branch = ref[len("refs/heads/"):]
        ref_spec = ["+" + ref + ":refs/remotes/origin/" + branch]
    # refs/pull/
    elif upper_ref.startswith('REFS/PULL/'):
        branch = ref[len("refs/pull/"):]
        ref_spec = ["+" + ref + ":refs/remotes/pull/" + branch]
    # refs/tags/
    else:
        ref_spec = ["+" + ref + ":" + ref]

    return (0, ref_spec)

def test_ref(git, ref, commit):
    """
    Tests whether the initial fetch created the ref at the expected commit
    """

    if not git:
        logger.error(LOG_TAG, "The 'git' arg for 'test_ref' method not set ")
        return (1, None)

    if not ref and not commit:
        logger.error(LOG_TAG, "The 'ref' and 'commit' args for 'test_ref' method cannot both be unset")
        return (1, None)

    # No SHA? Nothing to test
    if not commit:
        return (0, True)
    # SHA only?
    elif not ref:
        return (0, git.sha_exists(commit))

    upper_ref = ref.upper()

    # refs/heads/
    if upper_ref.startswith('REFS/HEADS/'):
        branch = ref[len("refs/heads/"):]
        return(0, git.branch_exists(True, "origin/" + branch) and
               commit == git.rev_parse("refs/remotes/origin/" + branch))

    # refs/pull/
    elif upper_ref.startswith('REFS/PULL/'):
        # Assume matches because fetched using the commit
        return (0, True)
    # refs/tags/
    elif upper_ref.startswith('REFS/TAGS/'):
        tag_name = ref[len("refs/tags/"):]
        return (0, git.tag_exists(tag_name) and commit == git.rev_parse(ref))
    # Unexpected
    else:
        logger.debug(LOG_TAG, "Unexpected ref format '" + ref + "' when testing ref info")
        return (0, True)
