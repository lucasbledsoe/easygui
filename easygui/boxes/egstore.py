"""

.. moduleauthor:: easygui developers and Stephen Raymond Ferg
.. default-domain:: py
.. highlight:: python

Version |release|
"""
import errno
import os
import pickle


class EgStore(object):
    """
    A class to support persistent storage.

    You can use ``EgStore`` to support the storage and retrieval
    of user settings for an EasyGui application.

    **Example A: define a class named Settings as a subclass of EgStore** ::

        class Settings(EgStore):
            def __init__(self, filename):  # filename is required
                # specify default values for variables that this application wants to remember
                self.user_id = ''
                self.target_server = ''

                # call super **after** setting defaults
                super(Settings, self).__init__(filename)

    **Example B: create settings, a persistent Settings object** ::

        settings = Settings('app_settings')
        settings.user_id = 'obama_barak'
        settings.targetServer = 'whitehouse1'
        settings.store()

        # run code that gets a new value for user_id, and persist the settings
        settings.user_id = 'biden_joe'
        settings.store()

    **Example C: recover the Settings instance, change an attribute, and store it again.** ::

        settings = Settings('app_settings')
        settings.user_id = 'vanrossum_g'
        settings.store()
    """

    def __init__(self, filename):
        """Initialize a store with the given filename and try to load stored values.
        If the filename doesn't exist yet, the restore is skipped.

        Only attributes defined here will be stored.
        Subclasses should initialize any attributes they want to store here, then call ``super``.

        :param filename: the file that backs this store for saving and loading
        """

        self._filename = filename

        try:
            self.restore()
        except IOError as e:
            if e.errno != errno.ENOENT:
                raise

    def restore(self):
        """
        Set the values of whatever attributes are recoverable
        from the pickle file.

        Populate the attributes (the __dict__) of the EgStore object
        from the attributes (the __dict__) of the pickled object.

        If the pickled object has attributes that have been initialized
        in the EgStore object, then those attributes of the EgStore object
        will be replaced by the values of the corresponding attributes
        in the pickled object.

        If the pickled object is missing some attributes that have
        been initialized in the EgStore object, then those attributes
        of the EgStore object will retain the values that they were
        initialized with.

        If the pickled object has some attributes that were not
        initialized in the EgStore object, then those attributes
        will be ignored.

        IN SUMMARY:

        After the recover() operation, the EgStore object will have all,
        and only, the attributes that it had when it was initialized.

        Where possible, those attributes will have values recovered
        from the pickled object.
        """
        with open(self._filename, 'rb') as f:
            store = pickle.load(f)

        self.__dict__.update((key, value) for key, value in store.__dict__.items() if key in self.__dict__)
        return self

    def store(self):
        """Save this store to a pickle file.
        All directories in :attr:`filename` must already exist.
        """

        with open(self._filename, 'wb') as f:
            pickle.dump(self, f)

    def kill(self):
        """Delete this store's file if it exists."""

        if os.path.isfile(self._filename):
            os.remove(self._filename)

    def __getstate__(self):
        state = self.__dict__.copy()
        del state['_filename']
        return state

    def __setstate__(self, state):
        if '_filename' in state:
            del state['_filename']

        self.__dict__.update(state)

    def __str__(self):
        """"Format this store as "key : value" pairs, one per line."""

        width = max(len(key) for key in self.__dict__ if key != '_filename')
        return '\n'.join('{0} : {1!r}'.format(key.ljust(width), value) for key, value in sorted(self.__dict__.keys()) if key != '_filename')

    def __repr__(self):
        return '{0}({1!r})'.format(self.__class__.__name__, self._filename)
